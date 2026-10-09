"""Bounded walk-forward lab. Train-only selection, explicit cash fallback."""
import argparse,hashlib,json
from dataclasses import replace
from pathlib import Path
from .fx_research import load_forex_csv,replay
from .market_book import BOOKS,default_config
from .market_signals import signal
from .pro_signals import FeatureCache,FAMILIES

def candidates(market):
    cfg=default_config(market)
    base=dict(stop_fraction=cfg.stop_fraction,reward_risk=2)
    return [dict(family=f,threshold=t,**base) for f in ('band_recovery','range_reversion') for t in (35,45)]+[
        dict(family='macd_swing',threshold=40,stop_fraction=s,reward_risk=2) for s in (cfg.stop_fraction/2,cfg.stop_fraction)]+[
        dict(family=f,threshold=t,**base) for f,t in [('trend',10),('rsi_pullback',40),('rsi2_reversion',10),('donchian',10)]]

def cost_estimate(market,stress=False):
    cfg=default_config(market)
    return ((.00015 if market=='forex' else .0005)+2*cfg.slippage_fraction+2*cfg.commission_fraction)*(2 if stress else 1)

def run(rows,start,market,symbol,params,cache,stress=False):
    cfg=replace(default_config(market),stop_fraction=params['stop_fraction'],reward_risk=params['reward_risk'])
    if stress:cfg=replace(cfg,commission_fraction=cfg.commission_fraction+.00005,slippage_fraction=cfg.slippage_fraction*2)
    cost=cost_estimate(market) # Frozen entry hurdle; execution costs alone are stressed.
    if params['family'] in FAMILIES:callback=cache.callback(params['family'],params['threshold'],market=='forex',cost)
    else:callback=lambda history,side:signal(history,params['family'],side,params['threshold'],market=='forex',cost)
    return replay(rows,start,config=cfg,book_class=BOOKS[market],symbol=symbol,
        spread_fraction=(.00015 if market=='forex' else .0005)*(2 if stress else 1),row_signal_fn=callback)

def select(scores):
    eligible=[s for s in scores if all(r['closed_trades']>=15 and r['net_pnl']>0 and (r['profit_factor'] or 0)>=1.1 for r in s['validation_folds']) and s['cost_stress']['net_pnl']>0]
    # Net return after costs comes before win rate; cash is a genuine alternative.
    return max(eligible,key=lambda s:(min(r['return_pct'] for r in s['validation_folds']),sum(r['net_pnl'] for r in s['validation_folds']))) if eligible else None

def evaluate(rows,market,symbol):
    if len(rows)<600 or symbol not in BOOKS[market].allowed_symbols:raise ValueError('Need 600+ bars and a supported symbol')
    cache=FeatureCache(rows);n=len(rows);cut=int(n*.7);edges=[int(n*.3),int(n*.5),cut]
    scores=[]
    for params in candidates(market):
        folds=[run(rows[:edges[i+1]],edges[i],market,symbol,params,cache) for i in range(2)]
        stressed=run(rows[:cut],edges[0],market,symbol,params,cache,True)
        scores.append(dict(parameters=params,validation_folds=folds,cost_stress=stressed))
    chosen=select(scores);baseline=candidates(market)[6]
    fixed=[dict(parameters=s['parameters'],later_period=run(rows,cut,market,symbol,s['parameters'],cache)) for s in scores]
    result=dict(market=market,symbol=symbol,rows=n,test_start=rows[cut]['timestamp'].isoformat(),test_end=rows[-1]['timestamp'].isoformat(),
        selection_rule='Ten declared candidates. Each of two training validation folds must have >=15 closed trades, positive net P/L and PF>=1.1; combined stressed validation must profit. Rank by worst-fold net return, then total net P/L. Otherwise cash.',
        selection_data_end=rows[cut-1]['timestamp'].isoformat(),validation_edges=edges,candidates=scores,selected_parameters=chosen['parameters'] if chosen else None,
        cash_fallback=chosen is None,cash_return_pct=0,baseline=run(rows,cut,market,symbol,baseline,cache),
        fixed_later_comparisons=fixed,auto_promotion=False,verified_70_percent=False,
        limitations='Exploratory historical evaluation; 2026 BTC/ETH/EURUSD periods already examined in earlier searches. Older downloaded 2025 data expands validation, not proof of future performance. Strategies are independently implemented approximations, not a run of Freqtrade or LEAN. Stock sample old/unadjusted; swaps, depth, partial fills and dividends absent. No future win probability.')
    if chosen:
        p=chosen['parameters'];result['selected_later']=run(rows,cut,market,symbol,p,cache);result['selected_later_stress']=run(rows,cut,market,symbol,p,cache,True)
        test_edges=[cut+(n-cut)*i//3 for i in range(4)]
        result['selected_later_folds']=[run(rows[:test_edges[i+1]],test_edges[i],market,symbol,p,cache) for i in range(3)]
        r=result['selected_later'];result['historical_acceptance']=r['closed_trades']>=100 and r['net_pnl']>0 and (r['profit_factor'] or 0)>=1.2 and result['selected_later_stress']['net_pnl']>0 and all(f['net_pnl']>0 for f in result['selected_later_folds'])
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--market',choices=BOOKS,required=True);p.add_argument('--symbol',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    result=evaluate(load_forex_csv(a.csv),a.market,a.symbol);result['input_sha256']=hashlib.sha256(Path(a.csv).read_bytes()).hexdigest()
    Path(a.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('candidates','fixed_later_comparisons')},indent=2))
if __name__=='__main__':main()
