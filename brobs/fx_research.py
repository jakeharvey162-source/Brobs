"""Chronological forex holdout replay. Historical evidence, never a forecast."""
import argparse
import csv
import json
import math
import tempfile
from datetime import timedelta
from pathlib import Path
from .fx import FXBook, FXConfig, utc
from .fx_signals import decide
from .history import load_csv

def load_forex_csv(path):
    # Normalize common public-data timestamp heading, retaining validation.
    with open(path,newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    if not rows:raise ValueError('Empty CSV')
    if 'timestamp' in rows[0]:return load_csv(path)
    if 'datetime' not in rows[0]:raise ValueError('timestamp or datetime header required')
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder)/'normalized.csv'
        with p.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['timestamp','open','high','low','close','volume']);w.writeheader()
            for row in rows:w.writerow({**{k:row[k] for k in ['open','high','low','close','volume']},'timestamp':row['datetime']})
        return load_csv(p)

def replay(rows, start, config=None, spread=.00015, mode='multi_agent'):
    if not 30 <= start < len(rows) or not math.isfinite(spread) or not 0 <= spread < .01:
        raise ValueError('Invalid start or spread')
    with tempfile.TemporaryDirectory() as folder:
        book=FXBook(Path(folder)/'test.db',config or FXConfig())
        def q(mid, timestamp):
            return {'EUR_USD':dict(bid=mid-spread/2,ask=mid+spread/2,timestamp=timestamp.isoformat(),tradeable=True)}
        for i in range(start,len(rows)):
            r=rows[i];t=utc(r['timestamp'])
            closes=[row['close'] for row in rows[max(0,i-200):i]]
            if mode=='multi_agent':action,votes=decide(closes)
            elif mode=='sma':
                from statistics import mean
                action='buy' if mean(closes[-8:])>mean(closes[-21:]) else 'sell';votes=[]
            else:raise ValueError('Unknown strategy')
            signals={'EUR_USD':dict(id=str(i),action=action,votes=votes,source='historical CSV')}
            book.process(q(r['open'],t),signals,f'{i}:open',t)
            p=book.snapshot()['positions'].get('EUR_USD')
            if p:
                long=p['units']>0
                hit_stop=r['low']-spread/2<=p['stop'] if long else r['high']+spread/2>=p['stop']
                hit_take=r['high']-spread/2>=p['take_profit'] if long else r['low']+spread/2<=p['take_profit']
                # If both levels touch, assume the stop first. Gap fills were handled at the open.
                if hit_stop or hit_take:
                    level=p['stop'] if hit_stop else p['take_profit']
                    mid=level+spread/2 if long else level-spread/2
                    at=t+timedelta(microseconds=1)
                    book.process(q(mid,at),{},f'{i}:intrabar',at)
            at=t+timedelta(microseconds=2)
            book.process(q(r['close'],at),{},f'{i}:close',at)
        # Liquidate the final position so metrics include all incurred costs.
        s=book.snapshot();p=s['positions'].get('EUR_USD')
        if p:
            at=utc(rows[-1]['timestamp'])+timedelta(microseconds=3)
            book.process(q(rows[-1]['close'],at),{'EUR_USD':dict(id='end',action='sell' if p['units']>0 else 'buy')},'liquidate',at)
        s=book.snapshot()
        return dict(**s['stats'],ending_equity=round(s['equity'],4),return_pct=round((s['equity']/s['initial_equity']-1)*100,4),
            max_drawdown_pct=round(s['max_drawdown']*100,4),halted_reason=s['halted_reason'])

def compare(rows, holdout=.3):
    if len(rows)<100 or not .2 <= holdout <= .5:raise ValueError('Need 100+ bars and a 20–50% holdout')
    start=int(len(rows)*(1-holdout))
    results={m:replay(rows,start,mode=m) for m in ['multi_agent','sma']}
    results['cash']=dict(return_pct=0,closed_trades=0,win_rate_pct=None)
    stress = replay(rows,start,config=FXConfig(commission_fraction=.00005),spread=.0003)
    fold_edges=[start+(len(rows)-start)*j//3 for j in range(4)]
    folds=[replay(rows[:fold_edges[j+1]],fold_edges[j]) for j in range(3)]
    return dict(dataset_rows=len(rows),train_bars=start,test_bars=len(rows)-start,
        test_start=rows[start]['timestamp'].isoformat(),test_end=rows[-1]['timestamp'].isoformat(),
        results=results,cost_stress=stress,chronological_test_folds=folds,assumptions=dict(account_currency='USD',leverage=1,spread=.00015,slippage_fraction=.00005,
        commission_fraction=0,swaps='not modeled',ambiguous_bar='stop first',signal_fill='next bar open',final_position='liquidated'),
        note='Fixed parameters, chronological holdout; no training or selection on holdout. One data vendor and one pair cannot prove future profitability. No statistical significance claimed.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--output');a=p.parse_args()
    result=compare(load_forex_csv(a.csv));text=json.dumps(result,indent=2,allow_nan=False)
    if a.output:Path(a.output).write_text(text+'\n')
    print(text)

if __name__=='__main__':main()
