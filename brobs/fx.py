"""USD-quoted forex paper accounting. No broker order endpoints exist in this module."""
import json
import math
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

PAIRS = ('EUR_USD', 'GBP_USD', 'AUD_USD', 'NZD_USD')

def utc(value):
    t = datetime.fromisoformat(value.replace('Z', '+00:00')) if isinstance(value, str) else value
    if not isinstance(t, datetime) or t.tzinfo is None:
        raise ValueError('Timezone-aware timestamp required')
    return t.astimezone(timezone.utc)

@dataclass(frozen=True)
class FXConfig:
    capital: float = 10000
    risk_fraction: float = .005
    stop_fraction: float = .005
    reward_risk: float = 2
    max_notional_fraction: float = .2
    daily_loss_fraction: float = .02
    drawdown_fraction: float = .1
    max_spread_fraction: float = .0008
    slippage_fraction: float = .00005
    commission_fraction: float = 0
    max_quote_age_seconds: float = 90

    def __post_init__(self):
        if any(not math.isfinite(v) for v in asdict(self).values()):
            raise ValueError('Non-finite configuration')
        if self.capital <= 0 or not 1 <= self.reward_risk <= 5 or not 1 <= self.max_quote_age_seconds <= 300:
            raise ValueError('Invalid capital, reward/risk or quote age')
        for key in ('risk_fraction', 'stop_fraction', 'max_notional_fraction', 'daily_loss_fraction', 'drawdown_fraction', 'max_spread_fraction'):
            if not 0 < getattr(self, key) <= .5: raise ValueError('Invalid ' + key)
        if self.risk_fraction > .02 or self.max_notional_fraction > .25:
            raise ValueError('Paper risk per trade capped at 2%; notional per pair at 25%')
        if any(not 0 <= v <= .01 for v in (self.slippage_fraction, self.commission_fraction)):
            raise ValueError('Invalid costs')


def validate_quotes(quotes, now, config, allowed_symbols=PAIRS):
    if not quotes: raise ValueError('No quotes')
    result = {}
    for symbol, quote in quotes.items():
        if symbol not in allowed_symbols: raise ValueError('Unsupported paper instrument')
        bid, ask = float(quote['bid']), float(quote['ask'])
        timestamp = utc(quote['timestamp'])
        age = (now - timestamp).total_seconds()
        if not math.isfinite(bid) or not math.isfinite(ask) or not 0 < bid <= ask:
            raise ValueError('Invalid bid/ask')
        if not -5 <= age <= config.max_quote_age_seconds: raise ValueError('Stale or future quote')
        if not quote.get('tradeable', False): raise ValueError('Market is not tradeable')
        result[symbol] = dict(bid=bid, ask=ask, timestamp=timestamp.isoformat(), tradeable=True)
    return result


def marked(state, quotes):
    floating = 0
    margin = 0
    for symbol, p in state['positions'].items():
        if symbol not in quotes: raise ValueError('Missing mark for open position: ' + symbol)
        mark = quotes[symbol]['bid'] if p['units'] > 0 else quotes[symbol]['ask']
        floating += p['units'] * (mark - p['entry'])
        margin += abs(p['units']) * p['entry']  # No leverage: reserve full notional.
    nav = state['balance'] + floating
    return dict(equity=nav, unrealized_pnl=floating, margin_used=margin, free_margin=nav-margin)


def statistics(trades):
    pnls = [t['pnl'] for t in trades]
    wins = sum(p > 1e-9 for p in pnls); losses = sum(p < -1e-9 for p in pnls)
    n = len(pnls); loss_total = -sum(p for p in pnls if p < 0)
    # Wilson interval: describes this sample, never a future win probability.
    interval = None
    if n:
        z = 1.96; rate = wins/n; den = 1+z*z/n
        center = (rate+z*z/(2*n))/den
        radius = z*math.sqrt(rate*(1-rate)/n+z*z/(4*n*n))/den
        interval = [round(100*(center-radius), 2), round(100*(center+radius), 2)]
    return dict(closed_trades=n, wins=wins, losses=losses, breakeven=n-wins-losses,
                win_rate_pct=round(100*wins/n, 2) if n else None,
                win_loss_ratio=round(wins/losses, 3) if losses else None,
                profit_factor=round(sum(p for p in pnls if p > 0)/loss_total, 3) if loss_total else None,
                net_pnl=round(sum(pnls), 4), sample_win_rate_95pct_interval=interval,
                evidence='insufficient_sample' if n < 100 else 'historical_sample_only')


class FXBook:
    profile = 'forex'
    quote_currency = 'USD'
    allowed_symbols = PAIRS

    def quantize_units(self, units):
        return math.floor(units)

    def permits_short(self, symbol):
        return True

    def __init__(self, path, config=None):
        self.path = str(path)
        self.config = config or FXConfig()
        with self.connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS fx_state (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS fx_events (event_id TEXT PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS fx_health (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS fx_trades (id INTEGER PRIMARY KEY, data TEXT NOT NULL)')
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT data FROM fx_state WHERE id=1').fetchone()
            if row and json.loads(row[0]).get('profile', 'forex') != self.profile:
                raise ValueError('Database asset profile differs. Use a separate database.')
            if row and json.loads(row[0])['config'] != asdict(self.config):
                raise ValueError('Database risk configuration differs. Use the same settings or a new database.')
            if not row:
                state = dict(profile=self.profile, quote_currency=self.quote_currency, balance=self.config.capital, initial_equity=self.config.capital, positions={},
                    peak=self.config.capital, day=None, day_equity=self.config.capital, halted_reason=None,
                    paused=False, signals={}, quotes={}, last_tick=None, config=asdict(self.config), max_drawdown=0)
                db.execute('INSERT INTO fx_state VALUES (1,?)', (json.dumps(state, allow_nan=False),))

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=15)
        try:
            with db: yield db
        finally: db.close()

    def snapshot(self):
        with self.connect() as db:
            db.execute('BEGIN')
            state = json.loads(db.execute('SELECT data FROM fx_state WHERE id=1').fetchone()[0])
            trades = [json.loads(r[0]) for r in db.execute('SELECT data FROM fx_trades ORDER BY id')]
            health_row = db.execute('SELECT data FROM fx_health WHERE id=1').fetchone()
            health = json.loads(health_row[0]) if health_row else {'status':'not_started'}
            events = [json.loads(r[0]) for r in db.execute('SELECT data FROM fx_events ORDER BY rowid DESC LIMIT 30')]
        state.setdefault('profile', self.profile)
        state.setdefault('quote_currency', self.quote_currency)
        values = marked(state, state['quotes']) if state['positions'] else dict(equity=state['balance'], unrealized_pnl=0, margin_used=0, free_margin=state['balance'])
        return dict(mode=f'LOCAL {self.profile.upper()} PAPER · {self.quote_currency} · NO LEVERAGE', **state, **values,
                    stats=statistics(trades), trades=trades[-100:], events=events, health=health)

    def health(self, status, source, error=None):
        payload = dict(status=status, source=source, timestamp=datetime.now(timezone.utc).isoformat())
        if error: payload['error'] = error
        with self.connect() as db:
            db.execute('INSERT INTO fx_health VALUES (1,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data',
                (json.dumps(payload, allow_nan=False),))

    def pause(self, paused=True):
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            state = json.loads(db.execute('SELECT data FROM fx_state WHERE id=1').fetchone()[0])
            state['paused'] = bool(paused)
            db.execute('UPDATE fx_state SET data=? WHERE id=1', (json.dumps(state, allow_nan=False),))

    def process(self, quotes, signals, event_id, now=None):
        now = utc(now or datetime.now(timezone.utc))
        quotes = validate_quotes(quotes, now, self.config, self.allowed_symbols)
        if not isinstance(event_id, str) or not 0 < len(event_id) <= 500: raise ValueError('Invalid event ID')
        for symbol, signal in signals.items():
            if symbol not in quotes or signal['action'] not in ('buy', 'sell', 'hold', 'close'):
                raise ValueError('Invalid signal')
            if not isinstance(signal['id'], str) or not 0 < len(signal['id']) <= 200: raise ValueError('Invalid signal ID')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT 1 FROM fx_events WHERE event_id=?', (event_id,)).fetchone():
                return dict(status='duplicate_tick', fills=[])
            state = json.loads(db.execute('SELECT data FROM fx_state WHERE id=1').fetchone()[0])
            if state['last_tick'] and now < utc(state['last_tick']): raise ValueError('Out-of-order tick')
            for symbol, q in quotes.items():
                if symbol in state['quotes'] and utc(q['timestamp']) < utc(state['quotes'][symbol]['timestamp']):
                    raise ValueError('Out-of-order quote')
            nav = marked(state, quotes)['equity']
            if state['day'] != now.date().isoformat():
                state['day'] = now.date().isoformat(); state['day_equity'] = nav
                if state['halted_reason'] == 'daily_loss': state['halted_reason'] = None
            fills = []; closed = set()
            def close(symbol, reason):
                p = state['positions'].pop(symbol); q = quotes[symbol]
                exit_price = q['bid']*(1-self.config.slippage_fraction) if p['units'] > 0 else q['ask']*(1+self.config.slippage_fraction)
                fee = abs(p['units'])*exit_price*self.config.commission_fraction
                pnl = p['units']*(exit_price-p['entry'])-fee-p['entry_fee']
                state['balance'] += pnl+p['entry_fee']
                trade = dict(symbol=symbol, side='long' if p['units'] > 0 else 'short', units=p['units'],
                    entry=p['entry'], exit=exit_price, pnl=pnl, opened_at=p['opened_at'], closed_at=now.isoformat(), reason=reason)
                db.execute('INSERT INTO fx_trades(data) VALUES (?)', (json.dumps(trade, allow_nan=False),))
                fills.append(dict(action='close', **trade)); closed.add(symbol)
            for symbol, p in list(state['positions'].items()):
                mark = quotes[symbol]['bid'] if p['units'] > 0 else quotes[symbol]['ask']
                stop = mark <= p['stop'] if p['units'] > 0 else mark >= p['stop']
                take = mark >= p['take_profit'] if p['units'] > 0 else mark <= p['take_profit']
                if stop or take: close(symbol, 'stop' if stop else 'take_profit')
            nav = marked(state, quotes)['equity']; state['peak'] = max(state['peak'], nav)
            dd = (state['peak']-nav)/state['peak']; state['max_drawdown'] = max(state['max_drawdown'], dd)
            if dd >= self.config.drawdown_fraction: state['halted_reason'] = 'max_drawdown'
            elif nav <= state['day_equity']*(1-self.config.daily_loss_fraction) and not state['halted_reason']:
                state['halted_reason'] = 'daily_loss'
            if state['halted_reason']:
                for symbol in list(state['positions']): close(symbol, 'risk_halt')
            for symbol, signal in signals.items():
                if state['signals'].get(symbol) == signal['id']: continue
                state['signals'][symbol] = signal['id']
                action = signal['action']; p = state['positions'].get(symbol)
                if p and (action == 'close' or (action == 'sell' and p['units'] > 0) or (action == 'buy' and p['units'] < 0)):
                    close(symbol, 'opposite_signal')
                if action in ('hold', 'close') or (action == 'sell' and not self.permits_short(symbol)) or state['paused'] or state['halted_reason'] or symbol in closed or symbol in state['positions']: continue
                q = quotes[symbol]
                if (q['ask']-q['bid'])/q['bid'] > self.config.max_spread_fraction: continue
                sign = 1 if action == 'buy' else -1
                entry = q['ask']*(1+self.config.slippage_fraction) if sign > 0 else q['bid']*(1-self.config.slippage_fraction)
                values = marked(state, quotes); nav = values['equity']
                per_unit_risk = entry*(self.config.stop_fraction+2*self.config.commission_fraction+self.config.slippage_fraction)
                units = self.quantize_units(min(nav*self.config.risk_fraction/per_unit_risk,
                    nav*self.config.max_notional_fraction/entry, max(0, values['free_margin'])/(entry*(1+self.config.commission_fraction))))
                if units <= 0: continue
                fee = units*entry*self.config.commission_fraction
                position = dict(units=sign*units, entry=entry, entry_fee=fee,
                    stop=entry*(1-sign*self.config.stop_fraction),
                    take_profit=entry*(1+sign*self.config.stop_fraction*self.config.reward_risk), opened_at=now.isoformat())
                state['balance'] -= fee; state['positions'][symbol] = position
                fills.append(dict(action='open', symbol=symbol, **position))
            state['quotes'] = quotes; state['last_tick'] = now.isoformat()
            values = marked(state, quotes)
            state['max_drawdown'] = max(state['max_drawdown'], (state['peak']-values['equity'])/state['peak'])
            payload = dict(status='halted' if state['halted_reason'] else 'paused' if state['paused'] else 'paper',
                timestamp=now.isoformat(), event_id=event_id, fills=fills, signals=signals, **values)
            db.execute('UPDATE fx_state SET data=? WHERE id=1', (json.dumps(state, allow_nan=False),))
            db.execute('INSERT INTO fx_events VALUES (?,?)', (event_id, json.dumps(payload, allow_nan=False)))
            return payload
