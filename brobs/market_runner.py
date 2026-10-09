"""Stock/USD or crypto/USDT local paper runner. Forex keeps its existing runner."""
import argparse
import hashlib
import json
import time
from dataclasses import replace
from datetime import datetime,timezone,timedelta
from .fx import utc
from .market_book import BOOKS,default_config
from .market_data import BinanceData,AlpacaData
from .market_signals import FAMILIES,signal


def tick(data,book,symbols,family='trend',now=None,grok_review=None,grok_request=None,threshold=None,evidence_report=None):
    fixed_now=now is not None
    now=utc(now or datetime.now(timezone.utc))
    if family not in FAMILIES or len(set(symbols))!=len(symbols):raise ValueError('Invalid strategy or duplicate instruments')
    if (grok_review or grok_request) and len(symbols)!=1:raise ValueError('Grok review requires exactly one symbol per runner')
    if data.market!=book.profile or not symbols or any(s not in book.allowed_symbols for s in symbols):raise ValueError('Market/ledger mismatch')
    if not data.market_open():
        book.health('closed',data.source,'Exchange closed; no new paper entries. Persisted stops require fresh quotes when reopened.')
        return dict(status='market_closed',fills=[])
    # Obtain executable marks independently of the signal history. Failed history
    # abstains for that symbol while stops still run on fresh quotes.
    quotes=data.quotes(symbols);positions=book.snapshot()['positions'];signals={}
    for symbol in symbols:
        try:
            rows=data.candles(symbol,now);last=utc(rows[-1]['timestamp']);age=(now-last).total_seconds()
            if not 3600<=age<=10800:raise ValueError('Signal candle is incomplete or stale')
            side=1 if symbol in positions else 0
            cost=.0005+2*book.config.slippage_fraction+2*book.config.commission_fraction
            action,votes=signal(rows,family,side,threshold=threshold,roundtrip_cost=cost)
            signals[symbol]=dict(id=family+':'+last.isoformat(),action=action,votes=votes,source=data.source)
            if action in ('buy','sell') and side==0 and evidence_report:
                from .evidence import gate as evidence_gate
                signals[symbol]=evidence_gate(signals[symbol],evidence_report,book.profile,symbol,family,threshold,book.config)
                action=signals[symbol]['action']
            if action in ('buy','sell') and side==0 and (grok_review or grok_request):
                from .grok_review import request_for,write_json,gate
                request=request_for(book,symbol,rows,signals[symbol],now)
                if grok_request:write_json(grok_request,request)
                signals[symbol]=gate(signals[symbol],request,grok_review,now)
        except (ValueError,KeyError,IndexError,OSError):
            signals[symbol]=dict(id='unavailable:'+now.isoformat(),action='hold',votes=[dict(agent='data_quality',action='veto',reason='No usable completed history; entry blocked, fresh-quote stops active')],source=data.source)
    key=json.dumps({s:quotes[s]['timestamp'] for s in sorted(quotes)},sort_keys=True)
    execution_now=now if fixed_now else datetime.now(timezone.utc)
    result=book.process(quotes,signals,'market:'+hashlib.sha256(key.encode()).hexdigest(),execution_now)
    book.health('ok',data.source)
    return result


class DemoData:
    def __init__(self,market):self.market=market;self.source='SYNTHETIC '+market.upper()+' DEMO — NOT MARKET PERFORMANCE'
    def market_open(self):return True
    def candles(self,symbol,now=None):
        now=utc(now or datetime.now(timezone.utc));start=now.replace(minute=0,second=0,microsecond=0)-timedelta(hours=200)
        base=100 if self.market=='stock' else 30000
        return [dict(timestamp=start+timedelta(hours=i),open=base*(1+i*.0005),high=base*(1+i*.0005+.0002),low=base*(1+i*.0005-.0002),close=base*(1+i*.0005),volume=100) for i in range(200)]
    def quotes(self,symbols):
        at=datetime.now(timezone.utc).isoformat();mid=109.95 if self.market=='stock' else 32985
        return {s:dict(bid=mid*.9999,ask=mid*1.0001,timestamp=at,tradeable=True) for s in symbols}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--market',choices=['stock','crypto'],required=True)
    p.add_argument('--symbols',nargs='+');p.add_argument('--db');p.add_argument('--strategy',choices=FAMILIES,default='trend');p.add_argument('--demo',action='store_true');p.add_argument('--once',action='store_true');p.add_argument('--interval',type=float,default=30)
    p.add_argument('--pause',action='store_true');p.add_argument('--resume',action='store_true')
    p.add_argument('--grok-review',help='Optional review JSON; missing/invalid review blocks entries')
    p.add_argument('--grok-request',help='Export current proposed entry evidence JSON (one symbol)')
    p.add_argument('--stop',type=float);p.add_argument('--reward-risk',type=float,default=2)
    p.add_argument('--capital',type=float,default=10000,help='Initial paper balance in the market quote currency; use a new database when changing capital')
    p.add_argument('--threshold',type=float);p.add_argument('--evidence-report',help='Optional local lab report; unaccepted/mismatched research blocks entry')
    p.add_argument('--cooldown-seconds',type=int);p.add_argument('--loss-streak-limit',type=int);p.add_argument('--loss-window-seconds',type=int)
    a=p.parse_args()
    if not 5<=a.interval<=3600:p.error('Interval must be 5–3600 seconds')
    if a.pause and a.resume:p.error('Choose pause or resume')
    if a.pause or a.resume:
        from .app import open_book
        book=open_book(a.db or f'brobs_{a.market}.db',a.market);book.pause(a.pause);print(json.dumps({'paused':a.pause}));return
    cfg=default_config(a.market)
    book=BOOKS[a.market](a.db or f'brobs_{a.market}.db',replace(cfg,capital=a.capital,stop_fraction=a.stop if a.stop is not None else cfg.stop_fraction,reward_risk=a.reward_risk))
    if any(v is not None for v in (a.cooldown_seconds,a.loss_streak_limit,a.loss_window_seconds)):
        from .protections import EntryProtection
        from dataclasses import asdict
        settings={**asdict(EntryProtection()),**book.snapshot().get('entry_protection',{})}
        for key in settings:
            value=getattr(a,key)
            if value is not None:settings[key]=value
        book.set_entry_protection(EntryProtection(**settings))
    symbols=tuple(sorted(set(a.symbols or [book.allowed_symbols[0]])|set(book.snapshot()['positions'])))
    if any(s not in book.allowed_symbols for s in symbols):p.error('Unsupported symbols: '+', '.join(book.allowed_symbols))
    data=DemoData(a.market) if a.demo else BinanceData() if a.market=='crypto' else AlpacaData()
    try:
        while True:
            try:print(json.dumps(tick(data,book,symbols,a.strategy,grok_review=a.grok_review,grok_request=a.grok_request,threshold=a.threshold,evidence_report=a.evidence_report),allow_nan=False),flush=True)
            except Exception as exc:
                book.health('error',data.source,type(exc).__name__)
                print(json.dumps(dict(status='error',error_type=type(exc).__name__,message='No new entries; check feed, connectivity and freshness.')),flush=True)
                if a.once:raise SystemExit(1)
            if a.once:break
            time.sleep(a.interval)
    except KeyboardInterrupt:print('Paper runner stopped; stored positions remain. Polling stops require a running, connected runner.')
if __name__=='__main__':main()
