"""Honest out-of-sample comparison with buy-and-hold and no-trade baselines."""
import json
from .backtest import backtest
from .models import Portfolio, Instrument, Market
from .risk import RiskEngine
from .paper import PaperBroker
from .agents import Coordinator
from .strategy import sma_signal, Signal

def _run(rows, symbol, market, capital, agent_mode=False):
    broker=PaperBroker(Portfolio(cash=capital,equity_at_day_start=capital),RiskEngine())
    ins=Instrument(symbol,Market(market))
    coordinator=Coordinator()
    curve=[]
    for i in range(21,len(rows)):
        p=rows[i]['open']
        marks={symbol:p}
        broker.apply_stops(marks)
        history=[r['close'] for r in rows[:i]]
        if agent_mode:
            action,_=coordinator.decide(history,broker.portfolio,broker.equity(marks))
        else:
            action=sma_signal(history).value
        if action=='buy':broker.buy(ins,p,marks)
        elif action=='sell':broker.sell(symbol,p)
        curve.append(broker.equity({symbol:rows[i]['close']}))
    peak=capital;dd=0
    for value in curve:
        peak=max(peak,value)
        dd=max(dd,(peak-value)/peak)
    final=broker.equity({symbol:rows[-1]['close']})
    return {'return_pct':round((final/capital-1)*100,3),'max_drawdown_pct':round(dd*100,3),'fills':len(broker.fills),'ending_equity':round(final,2)}

def compare(rows,symbol='ASSET',market='crypto',capital=10000,holdout_fraction=0.3):
    if len(rows)<100 or capital<=0:raise ValueError('Need 100+ bars and positive capital')
    if not 0.2<=holdout_fraction<=0.5:raise ValueError('Holdout must be 20%-50%')
    split=int(len(rows)*(1-holdout_fraction))
    # Include warmup history before test period, but never use future test candles.
    test=rows[split-21:]
    sma=_run(test,symbol,market,capital)
    agents=_run(test,symbol,market,capital,True)
    first=rows[split]['open'];last=rows[-1]['close']
    # Hold baseline pays simulated entry and exit costs, matching PaperBroker defaults.
    entry=first*1.0005;exit=last*0.9995
    qty=capital/(entry*1.001)
    hold_end=capital-qty*entry*1.001+qty*exit*0.999
    hold_return=(hold_end/capital-1)*100
    best=max(agents['return_pct'],sma['return_pct'],hold_return,0)
    return {'disclaimer':'Historical simulation only; not a verified edge or forecast','train_bars':split,'test_bars':len(rows)-split,'test_start':rows[split]['timestamp'].isoformat(),'results':{'multi_agent':agents,'sma':sma,'buy_hold':{'return_pct':round(hold_return,3)},'cash':{'return_pct':0}},'winner_in_this_sample':max([('multi_agent',agents['return_pct']),('sma',sma['return_pct']),('buy_hold',hold_return),('cash',0)],key=lambda x:x[1])[0],'profitability_ratio':None,'note':'Profitability ratio requires a defined metric, sufficient independent periods and real execution evidence.'}

def main():
    import argparse
    from .history import load_csv
    p=argparse.ArgumentParser()
    p.add_argument('--csv',required=True);p.add_argument('--market',choices=['crypto','forex','stock'],required=True)
    p.add_argument('--symbol',required=True);p.add_argument('--cash',type=float,default=10000)
    a=p.parse_args()
    print(json.dumps(compare(load_csv(a.csv),a.symbol,a.market,a.cash),indent=2))
if __name__=='__main__':main()
