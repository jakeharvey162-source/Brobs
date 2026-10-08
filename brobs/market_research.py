"""Multi-market, train-selected exploration. No profit guarantees or auto-promotion."""
import argparse
import json
from dataclasses import replace
from functools import partial
from pathlib import Path
from .fx_research import replay,load_forex_csv
from .history import load_csv
from .market_book import BOOKS,default_config
from .market_signals import signal


def candidates(market):
    stops=(.002,.004) if market=='forex' else (.02,.04) if market=='stock' else (.01,.02)
    return [dict(family='rsi2_reversion',threshold=t,stop_fraction=s,reward_risk=1.5) for t in (5,10,20) for s in stops]+[
        dict(family='rsi_pullback',threshold=t,stop_fraction=stops[0],reward_risk=1.5) for t in (35,40)]+[
        dict(family=f,threshold=10,stop_fraction=stops[0],reward_risk=2) for f in ('donchian','trend')]


def run(rows,start,market,symbol,params,stress=False):
    cfg=replace(default_config(market),stop_fraction=params['stop_fraction'],reward_risk=params['reward_risk'])
    if stress:cfg=replace(cfg,commission_fraction=cfg.commission_fraction+.00005,slippage_fraction=cfg.slippage_fraction*2)
    return replay(rows,start,config=cfg,book_class=BOOKS[market],symbol=symbol,
        spread_fraction=(.00015 if market=='forex' else .0005)*(2 if stress else 1),
        row_signal_fn=lambda history,side:signal(history,params['family'],side,params['threshold'],market=='forex'))


def evaluate(rows,market,symbol):
    if len(rows)<350 or symbol not in BOOKS[market].allowed_symbols:raise ValueError('Need 350+ bars and supported symbol')
    cut=int(len(rows)*.7);inner=max(100,int(cut*.6))
    scores=[dict(parameters=p,validation=run(rows[:cut],inner,market,symbol,p)) for p in candidates(market)]
    eligible=[s for s in scores if s['validation']['closed_trades']>=30 and s['validation']['net_pnl']>0 and (s['validation']['profit_factor'] or 0)>=1.2]
    chosen=max(eligible,key=lambda s:(s['validation']['win_rate_pct'],s['validation']['profit_factor'])) if eligible else None
    result=dict(market=market,symbol=symbol,rows=len(rows),train_bars=cut,test_bars=len(rows)-cut,
        train_start=rows[0]['timestamp'].isoformat(),test_start=rows[cut]['timestamp'].isoformat(),test_end=rows[-1]['timestamp'].isoformat(),
        candidates=scores,selected=chosen,selection_rule='Highest validation win rate with 30+ closed trades, positive P/L and profit factor >=1.2, only first 70% of bars used for selection.',
        auto_promotion=False,verified_target_70_or_80=False,
        caveat='Exploratory selection among 10 candidates. Prior EURUSD period already examined. Fresh forward paper results and larger samples needed; no market-wide/future probability claim. USD stock/FX and USDT crypto balances are separate. No swaps/dividends/partial fills/liquidity constraints. Stock sample is old and unadjusted; corporate actions can invalidate equity results.')
    baseline=dict(family='trend',threshold=10,stop_fraction=default_config(market).stop_fraction,reward_risk=default_config(market).reward_risk)
    result['baseline_parameters']=baseline
    result['baseline']=run(rows,cut,market,symbol,baseline)
    result['baseline_cost_stress']=run(rows,cut,market,symbol,baseline,True)
    if chosen:
        p=chosen['parameters'];result['later_period']=run(rows,cut,market,symbol,p);result['cost_stress']=run(rows,cut,market,symbol,p,True)
        edges=[cut+(len(rows)-cut)*i//3 for i in range(4)]
        result['later_folds']=[run(rows[:edges[i+1]],edges[i],market,symbol,p) for i in range(3)]
        r=result['later_period'];stress=result['cost_stress']
        result['historical_70_gate_passed']=r['closed_trades']>=100 and r['win_rate_pct']>=70 and r['net_pnl']>0 and (r['profit_factor'] or 0)>=1.2 and stress['net_pnl']>0 and all(f['net_pnl']>0 for f in result['later_folds'])
    else:result['rejection']='No candidate met the training validation sample/profit gates; no replacement selected.'
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--market',choices=BOOKS,required=True);p.add_argument('--symbol',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    r=evaluate(load_forex_csv(a.csv),a.market,a.symbol);Path(a.output).write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='candidates'},indent=2))
if __name__=='__main__':main()
