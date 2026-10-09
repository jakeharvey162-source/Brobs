"""Optional fail-closed local research gate; no automated strategy promotion."""
from .grok_review import read_json
from math import isfinite

def gate(proposal,path,market,symbol,family,threshold,config):
    try:
        report=read_json(path);p=report['selected_parameters'];later=report['selected_later'];stress=report['selected_later_stress'];folds=report['selected_later_folds']
        metrics=[later['closed_trades'],later['net_pnl'],later['profit_factor'],stress['net_pnl']]+[f['net_pnl'] for f in folds]
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(v) for v in metrics):raise ValueError('Invalid evidence metrics')
        if not isinstance(later['closed_trades'],int):raise ValueError('Invalid trade count')
        if report['market']!=market or report['symbol']!=symbol or report.get('historical_acceptance') is not True:raise ValueError('No accepted evidence')
        effective=threshold if threshold is not None else 40 if family in ('rsi_pullback','band_recovery','range_reversion','macd_swing') else 20 if family=='grok_consensus' else 10
        if p!=dict(family=family,threshold=effective,stop_fraction=config.stop_fraction,reward_risk=config.reward_risk):raise ValueError('Parameters differ')
        if later['closed_trades']<100 or later['net_pnl']<=0 or (later['profit_factor'] or 0)<1.2 or stress['net_pnl']<=0 or len(folds)!=3 or any(f['net_pnl']<=0 for f in folds):raise ValueError('Performance gates fail')
        approved=True;reason='Historical gates passed for matching local profile; future profit remains unverified'
    except (OSError,ValueError,KeyError,TypeError,AttributeError):
        approved=False;reason='No matching accepted research profile; remain in cash for new entries'
    return {**proposal,'action':proposal['action'] if approved else 'hold',
        'votes':proposal.get('votes',[])+[dict(agent='research_evidence',action='permit' if approved else 'veto',reason=reason)]}
