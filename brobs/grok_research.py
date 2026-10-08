"""Predeclared six-candidate Grok-method exploration with chronological tests."""
import argparse,json
from pathlib import Path
from .market_research import run
from .market_book import default_config
from .fx_research import load_forex_csv

def evaluate(rows,market,symbol):
    cut=int(len(rows)*.7);inner=int(cut*.6)
    stop=default_config(market).stop_fraction
    parameters=[dict(family='grok_consensus',threshold=t,stop_fraction=s,reward_risk=2) for t in (10,20,30) for s in (stop/2,stop)]
    scores=[dict(parameters=p,validation=run(rows[:cut],inner,market,symbol,p)) for p in parameters]
    eligible=[s for s in scores if s['validation']['closed_trades']>=30 and s['validation']['net_pnl']>0 and (s['validation']['profit_factor'] or 0)>=1.2]
    selected=max(eligible,key=lambda s:(s['validation']['win_rate_pct'],s['validation']['profit_factor'])) if eligible else None
    # Fixed threshold20/default stop is evaluated even when training rejects all.
    fixed=dict(family='grok_consensus',threshold=20,stop_fraction=stop,reward_risk=2)
    baseline=dict(family='trend',threshold=10,stop_fraction=stop,reward_risk=2)
    result=dict(market=market,symbol=symbol,rows=len(rows),test_start=rows[cut]['timestamp'].isoformat(),test_end=rows[-1]['timestamp'].isoformat(),
        candidates=scores,selected=selected,fixed_parameters=fixed,fixed_later=run(rows,cut,market,symbol,fixed),
        fixed_cost_stress=run(rows,cut,market,symbol,fixed,True),baseline=run(rows,cut,market,symbol,baseline),
        auto_promotion=False,verified_70_percent=False,actual_grok_model_backtested=False,
        note='Independent deterministic multi-timeframe method, not historical LLM answers. Six training candidates declared before ETH test. BTC/EURUSD previously inspected; exploratory only. No future probability claim. Default unchanged.')
    if selected:
        p=selected['parameters'];result['selected_later']=run(rows,cut,market,symbol,p);result['selected_cost_stress']=run(rows,cut,market,symbol,p,True)
    else:result['rejection']='No variant passed 30 closed validation trades, positive net P/L and PF>=1.2.'
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--market',choices=['forex','stock','crypto'],required=True);p.add_argument('--symbol',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    result=evaluate(load_forex_csv(a.csv),a.market,a.symbol);Path(a.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='candidates'},indent=2))
if __name__=='__main__':main()
