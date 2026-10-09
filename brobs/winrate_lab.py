"""Fixed RSI2 experiment; historical win-rate diagnostics, never a forecast."""
import argparse
import hashlib
import json
from dataclasses import replace
from math import sqrt
from pathlib import Path
from statistics import mean
from .fx_research import load_forex_csv, replay
from .market_book import BOOKS, default_config
from .market_signals import rsi
from .strategy_lab import select

def sample_check(stats, target=.70):
    """Recompute from counts; no reliance on rounded/reported percentages."""
    n, wins = stats['closed_trades'], stats['wins']
    if (type(n) is not int or type(wins) is not int or n < 0 or not 0 <= wins <= n
            or not 0 < target < 1):
        raise ValueError('Invalid counts or target')
    interval = None
    if n:
        z=1.96; p=wins/n; den=1+z*z/n
        center=(p+z*z/(2*n))/den
        radius=z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
        interval=[center-radius,center+radius]
    return dict(target_pct=target*100,closed_trades=n,wins=wins,
        observed_pct=100*wins/n if n else None,
        wilson_95pct_interval=[100*v for v in interval] if interval else None,
        historical_count_gate=n>=100 and interval[0]>target,
        verified_future_probability=False,
        caveat='Descriptive binomial interval assumes independent trades; market regimes, correlated trades and repeated searches weaken interpretation. Count gate alone does not certify a strategy.')

class RSI2Cache:
    """Match runner's previous 500 bars exactly; immutable prefix features."""
    def __init__(self,rows):
        self.values={}
        for i,row in enumerate(rows):
            closes=[r['close'] for r in rows[max(0,i-499):i+1]]
            if len(closes)>=100:
                self.values[row['timestamp']]=(closes[-1],mean(closes[-100:]),mean(closes[-5:]),rsi(closes,2))
    def callback(self,threshold,allow_short):
        def decide(history,side):
            f=self.values.get(history[-1]['timestamp'])
            if f is None:return 'hold',[]
            last,regime,fast,strength=f; action='hold'
            if side>0 and (last>=fast or strength>=70):action='close'
            elif side<0 and (last<=fast or strength<=30):action='close'
            elif not side:
                if last>regime and strength<threshold:action='buy'
                elif allow_short and last<regime and strength>100-threshold:action='sell'
            return action,[]
        return decide

def candidates(market):
    stop=default_config(market).stop_fraction
    return [dict(family='rsi2_reversion',threshold=t,stop_fraction=s,reward_risk=rr)
        for t in (5,10,20,35) for s in (stop/2,stop) for rr in (1,2)]

def run(rows,start,market,symbol,p,cache,stress=False):
    cfg=replace(default_config(market),stop_fraction=p['stop_fraction'],reward_risk=p['reward_risk'])
    if stress:cfg=replace(cfg,commission_fraction=cfg.commission_fraction+.00005,slippage_fraction=cfg.slippage_fraction*2)
    return replay(rows,start,config=cfg,book_class=BOOKS[market],symbol=symbol,
        spread_fraction=(.00015 if market=='forex' else .0005)*(2 if stress else 1),
        row_signal_fn=cache.callback(p['threshold'],market=='forex'))

def evaluate(rows,market,symbol):
    if len(rows)<600 or symbol not in BOOKS[market].allowed_symbols:raise ValueError('Need 600+ bars and supported symbol')
    cache=RSI2Cache(rows);n=len(rows);cut=int(n*.7);edges=[int(n*.3),int(n*.5),cut]
    scores=[]
    for p in candidates(market):
        folds=[run(rows[:edges[i+1]],edges[i],market,symbol,p,cache) for i in range(2)]
        scores.append(dict(parameters=p,validation_folds=folds,cost_stress=run(rows[:cut],edges[0],market,symbol,p,cache,True)))
    chosen=select(scores) # Uses training folds only; later results never select.
    fixed=[]
    for s in scores:
        later=run(rows,cut,market,symbol,s['parameters'],cache)
        fixed.append(dict(parameters=s['parameters'],later_period=later,sample_check=sample_check(later)))
    result=dict(market=market,symbol=symbol,rows=n,selection_data_end=rows[cut-1]['timestamp'].isoformat(),
        test_start=rows[cut]['timestamp'].isoformat(),test_end=rows[-1]['timestamp'].isoformat(),
        selection_rule='16 declared RSI2 profiles; two training folds each >=15 trades, positive net P/L, PF>=1.1; stressed training positive; rank worst-fold return. Otherwise cash.',
        candidates=scores,selected_parameters=chosen['parameters'] if chosen else None,
        fixed_later_comparisons=fixed,cash_fallback=chosen is None,historical_acceptance=False,
        verified_70_percent=False,auto_promotion=False,
        limitations='These periods were inspected in earlier experiments: exploratory reused data, not untouched validation. Fees/spread/slippage included; ambiguous OHLC stop first; no news/sentiment reconstruction, broker partial fills, funding or swaps. Real Grok outputs were not replayed. Future >70% win probability cannot be inferred.')
    if chosen:
        p=chosen['parameters'];later=run(rows,cut,market,symbol,p,cache)
        result['selected_later']=later;result['selected_later_stress']=run(rows,cut,market,symbol,p,cache,True)
        test_edges=[cut+(n-cut)*i//3 for i in range(4)]
        result['selected_later_folds']=[run(rows[:test_edges[i+1]],test_edges[i],market,symbol,p,cache) for i in range(3)]
        result['selected_sample_check']=sample_check(later)
        result['exploratory_target_gates_pass']=sample_check(later)['historical_count_gate'] and later['net_pnl']>0 and (later['profit_factor'] or 0)>=1.2 and result['selected_later_stress']['net_pnl']>0 and all(f['net_pnl']>0 for f in result['selected_later_folds'])
        # Even a pass remains exploratory because the test period was reused.
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--csv',required=True);p.add_argument('--market',choices=BOOKS,required=True)
    p.add_argument('--symbol',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    result=evaluate(load_forex_csv(a.csv),a.market,a.symbol)
    result['input_sha256']=hashlib.sha256(Path(a.csv).read_bytes()).hexdigest()
    Path(a.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(market=a.market,symbol=a.symbol,selected=result['selected_parameters'],verified_70_percent=False)))
if __name__=='__main__':main()
