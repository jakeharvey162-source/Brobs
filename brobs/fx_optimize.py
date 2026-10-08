"""Small, reproducible train-only candidate selection; exploratory evaluation."""
import argparse
import json
from functools import partial
from pathlib import Path
from .fx import FXConfig
from .fx_candidates import reversion
from .fx_research import load_forex_csv, replay


def evaluate(rows):
    if len(rows)<500:raise ValueError('Need at least 500 bars')
    cut=int(len(rows)*.7);inner=int(cut*.6)
    candidates=[]
    for period in (20,40):
        for deviation in (1.5,2.0,2.5):
            for stop in (.002,.004):
                params=dict(period=period,deviation=deviation,stop_fraction=stop,reward_risk=1)
                validation=replay(rows[:cut],inner,config=FXConfig(stop_fraction=stop,reward_risk=1),signal_fn=partial(reversion,period=period,deviation=deviation))
                candidates.append(dict(parameters=params,validation=validation))
    eligible=[c for c in candidates if c['validation']['closed_trades']>=40 and c['validation']['net_pnl']>0 and (c['validation']['profit_factor'] or 0)>1 and c['validation']['max_drawdown_pct']<2]
    if not eligible:raise ValueError('No candidate meets the selection criteria; keep existing strategy')
    chosen=max(eligible,key=lambda c:(c['validation']['win_rate_pct'],c['validation']['profit_factor']))
    return evaluate_selected(rows,candidates,chosen)


def evaluate_selected(rows,candidates,chosen):
    cut=int(len(rows)*.7);params=chosen['parameters']
    fn=partial(reversion,period=params['period'],deviation=params['deviation'])
    cfg=FXConfig(stop_fraction=params['stop_fraction'],reward_risk=params['reward_risk'])
    later=replay(rows,cut,config=cfg,signal_fn=fn)
    stress=replay(rows,cut,config=FXConfig(stop_fraction=params['stop_fraction'],reward_risk=params['reward_risk'],commission_fraction=.00005),spread=.0003,signal_fn=fn)
    edges=[cut+(len(rows)-cut)*j//3 for j in range(4)]
    folds=[replay(rows[:edges[j+1]],edges[j],config=cfg,signal_fn=fn) for j in range(3)]
    return dict(selection_rule='Highest validation win rate among 40+ trades, positive net P/L, profit factor >1 and drawdown <2%; 12 candidates, training partition only',
        candidates=candidates,selected=chosen,later_period=later,cost_stress=stress,later_folds=folds,
        train_bars=cut,validation_start=int(cut*.6),later_start=rows[cut]['timestamp'].isoformat(),later_end=rows[-1]['timestamp'].isoformat(),
        caveat='Exploratory, not a pristine holdout: the later period was previously examined for the original strategy. Selection uses training only, but fresh future forward-paper data is required. No future win rate or 70–80% guarantee. Selection bias and only one vendor/pair; swaps not modeled. Closed-bar signals, next-open execution, bid/ask costs, stop-first ambiguous bars, 1:1 target/stop, no leverage.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--csv',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    result=evaluate(load_forex_csv(args.csv));Path(args.output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='candidates'},indent=2))

if __name__=='__main__':main()
