"""Automated practice-data/local-paper runner. Never sends broker orders."""
import argparse
import hashlib
import json
import time
from math import isfinite
from datetime import datetime, timezone, timedelta
from .fx import FXBook, FXConfig, PAIRS, utc
from .fx_signals import decide
from .oanda_practice import PracticeData

GRANULARITY_SECONDS = {'M5':300, 'M15':900, 'H1':3600, 'H4':14400, 'D':86400}

def tick(data, book, pairs=('EUR_USD',), granularity='H1', now=None, use_ml=False, family='trend', grok_review=None, grok_request=None,threshold=None,evidence_report=None):
    try:return _signal_tick(data,book,pairs,granularity,now,use_ml,family,grok_review,grok_request,threshold,evidence_report)
    except Exception:
        # A failed signal/account request must not suppress existing local stops.
        # This recovery has no entry signals, never uses stored/stale prices,
        # and preserves the original error for callers/health monitoring.
        if isinstance(book,FXBook) and book.profile=='forex':
            try:
                positions=book.snapshot()['positions']
                if positions:
                    quotes=data.quotes(tuple(sorted(positions)))
                    key=json.dumps({s:quotes[s]['timestamp'] for s in sorted(positions)},sort_keys=True)
                    book.process(quotes,{},'fx:safety:'+hashlib.sha256(key.encode()).hexdigest(),now or datetime.now(timezone.utc))
            except Exception:pass # Missing/future/stale marks cannot invent a fill.
        raise

def _signal_tick(data, book, pairs=('EUR_USD',), granularity='H1', now=None, use_ml=False, family='trend', grok_review=None, grok_request=None,threshold=None,evidence_report=None):
    fixed_now = now is not None
    now = utc(now or datetime.now(timezone.utc))
    if granularity not in GRANULARITY_SECONDS or not pairs or any(p not in PAIRS for p in pairs):
        raise ValueError('Unsupported granularity or USD-quoted pair')
    if len(set(pairs)) != len(pairs):
        raise ValueError('Duplicate trading pairs are not allowed')
    from .market_signals import FAMILIES
    if family not in FAMILIES or (family!='trend' and granularity!='H1'):raise ValueError('Additional strategies require H1')
    if family!='trend' and use_ml:raise ValueError('ML veto is available only for the original trend strategy')
    if (grok_review or grok_request) and len(pairs)!=1:raise ValueError('Grok review requires one pair')
    summary = data.account_summary()
    if summary.get('currency') != 'USD': raise ValueError('USD practice account required; currency conversion is not implemented')
    signals = {}
    for pair in pairs:
        rows = data.candles(instrument=pair, granularity=granularity, count=500 if family!='trend' else 200)
        if not isinstance(rows, (list, tuple)) or len(rows) < 50:
            raise ValueError('Insufficient completed candle history for '+pair)
        if any(not isinstance(row, dict) or 'timestamp' not in row or 'close' not in row for row in rows):
            raise ValueError('Malformed candle history for '+pair)
        previous = None
        for row in rows:
            price = row['close']
            if not isinstance(price, (int, float)) or isinstance(price, bool) or not isfinite(price) or price <= 0:
                raise ValueError('Invalid candle close for '+pair)
            candle_time = utc(row['timestamp'])
            if previous is not None and candle_time <= previous:
                raise ValueError('Unsorted or duplicate candles for '+pair)
            previous = candle_time
        last = previous
        age = (now-last).total_seconds()
        if age < GRANULARITY_SECONDS[granularity] or age > GRANULARITY_SECONDS[granularity]*3:
            raise ValueError('Incomplete, stale or future signal candle')
        action, votes = decide([r['close'] for r in rows], use_ml=use_ml)
        position=book.snapshot()['positions'].get(pair) if family!='trend' or grok_review or grok_request or evidence_report else None
        side=1 if position and position['units']>0 else -1 if position else 0
        if family!='trend':
            from .market_signals import signal
            cost=.00015+2*book.config.slippage_fraction+2*book.config.commission_fraction
            action,votes=signal(rows,family,side,threshold=threshold,allow_short=True,roundtrip_cost=cost)
        signals[pair] = dict(id=(family+':' if family!='trend' else '')+granularity+':'+last.isoformat(), action=action, votes=votes,
            source=getattr(data, 'source', 'OANDA practice market data'))
        if action in ('buy','sell') and side==0 and evidence_report:
            from .evidence import gate as evidence_gate
            signals[pair]=evidence_gate(signals[pair],evidence_report,'forex',pair,family,threshold,book.config)
            action=signals[pair]['action']
        if action in ('buy','sell') and side==0 and (grok_review or grok_request):
            from .grok_review import request_for,write_json,gate
            request=request_for(book,pair,rows,signals[pair],now)
            if grok_request:
                try:write_json(grok_request,request)
                except OSError:
                    signals[pair]={**signals[pair],'id':signals[pair]['id']+':export_failed','action':'hold'}
            signals[pair]=gate(signals[pair],request,grok_review,now)
    quotes = data.quotes(pairs)
    if not isinstance(quotes, dict) or any(pair not in quotes or not isinstance(quotes[pair], dict) or not quotes[pair].get('timestamp') for pair in pairs):
        raise ValueError('Missing or malformed market quotes')
    key = json.dumps({s:quotes[s]['timestamp'] for s in sorted(pairs)}, sort_keys=True)
    event_id = 'fx:'+hashlib.sha256(key.encode()).hexdigest()
    execution_now = now if fixed_now else datetime.now(timezone.utc)
    result = book.process(quotes, signals, event_id, execution_now)
    book.health('ok', getattr(data, 'source', 'OANDA practice market data'))
    return result

class DemoData:
    source = 'SYNTHETIC DEMO — NOT REAL MARKET PERFORMANCE'
    def account_summary(self): return {'currency':'USD'}
    def candles(self, instrument, granularity='H1', count=200):
        seconds = GRANULARITY_SECONDS[granularity]
        t = datetime.now(timezone.utc)
        current = datetime.fromtimestamp(int(t.timestamp())//seconds*seconds, timezone.utc)
        return [dict(timestamp=current-timedelta(seconds=seconds*(count-i)), open=1.08+i*.00005,high=1.0801+i*.00005,low=1.0799+i*.00005,close=1.08+i*.00005,volume=100) for i in range(count)]
    def quotes(self, pairs):
        t = datetime.now(timezone.utc).isoformat()
        return {p:dict(bid=1.0899, ask=1.0901, timestamp=t, tradeable=True) for p in pairs}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', default='brobs_fx.db');p.add_argument('--pairs', nargs='+', choices=PAIRS, default=['EUR_USD'])
    p.add_argument('--granularity', choices=tuple(GRANULARITY_SECONDS), default='H1')
    p.add_argument('--interval', type=float, default=30);p.add_argument('--once', action='store_true')
    p.add_argument('--ml-veto', action='store_true', help='Optional local sklearn direction vote; not benchmark-validated')
    from .market_signals import FAMILIES
    p.add_argument('--strategy',choices=FAMILIES,default='trend')
    p.add_argument('--stop',type=float,default=.005);p.add_argument('--reward-risk',type=float,default=2)
    p.add_argument('--threshold',type=float);p.add_argument('--evidence-report')
    p.add_argument('--cooldown-seconds',type=int);p.add_argument('--loss-streak-limit',type=int);p.add_argument('--loss-window-seconds',type=int)
    p.add_argument('--grok-request');p.add_argument('--grok-review')
    p.add_argument('--demo', action='store_true');p.add_argument('--capital', type=float, default=10000)
    p.add_argument('--risk', type=float, default=.005);p.add_argument('--daily-loss', type=float, default=.02)
    p.add_argument('--pause', action='store_true');p.add_argument('--resume', action='store_true')
    a=p.parse_args()
    if not 5 <= a.interval <= 3600:p.error('Interval must be 5–3600 seconds')
    if a.pause or a.resume:
        if a.pause and a.resume:p.error('Choose pause or resume')
        from .app import open_book
        book=open_book(a.db,'forex');book.pause(a.pause);print(json.dumps({'paused':a.pause}));return
    config=FXConfig(capital=a.capital, risk_fraction=a.risk, daily_loss_fraction=a.daily_loss,stop_fraction=a.stop,reward_risk=a.reward_risk)
    book=FXBook(a.db,config)
    if any(v is not None for v in (a.cooldown_seconds,a.loss_streak_limit,a.loss_window_seconds)):
        from .protections import EntryProtection
        existing=book.snapshot().get('entry_protection',{})
        from dataclasses import asdict
        settings={**asdict(EntryProtection()),**existing}
        for key in settings:
            value=getattr(a,key)
            if value is not None:settings[key]=value
        book.set_entry_protection(EntryProtection(**settings))
    data=DemoData() if a.demo else PracticeData()
    # Prevent missing pair marks after restarting with different CLI arguments.
    pairs=tuple(sorted(set(a.pairs)|set(book.snapshot()['positions'])))
    try:
        while True:
            try:
                print(json.dumps(tick(data,book,pairs,a.granularity,use_ml=a.ml_veto,family=a.strategy,grok_request=a.grok_request,grok_review=a.grok_review,threshold=a.threshold,evidence_report=a.evidence_report),allow_nan=False),flush=True)
            except Exception as exc:
                # Do not log transport messages or request bodies that may contain secrets.
                book.health('error',data.source if a.demo else 'OANDA practice market data',type(exc).__name__)
                print(json.dumps({'status':'error','error_type':type(exc).__name__,'message':'No new entries; check account, connectivity and data freshness.'}),flush=True)
                if a.once:raise SystemExit(1)
            if a.once:break
            time.sleep(a.interval)
    except KeyboardInterrupt:print('Runner stopped. Paper positions remain persisted; stops require the runner to be running.')

if __name__=='__main__':main()
