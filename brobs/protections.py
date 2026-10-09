"""Optional durable entry guards. They never suppress exits or change sizing."""
from dataclasses import dataclass,asdict
from math import isfinite
from .fx import utc

@dataclass(frozen=True)
class EntryProtection:
    cooldown_seconds:int=0
    loss_streak_limit:int=0
    loss_window_seconds:int=86400
    def __post_init__(self):
        if any(isinstance(v,bool) or not isinstance(v,int) for v in asdict(self).values()):raise ValueError('Protection values must be integers')
        if not 0<=self.cooldown_seconds<=86400 or not 0<=self.loss_streak_limit<=20 or not 300<=self.loss_window_seconds<=604800:raise ValueError('Invalid entry protection')

def reason(trades,now,policy):
    if not trades:return None
    latest=trades[0]
    if (utc(now)-utc(latest['closed_at'])).total_seconds()<policy.cooldown_seconds:return 'cooldown'
    if policy.loss_streak_limit:
        streak=0
        for trade in trades:
            age=(utc(now)-utc(trade['closed_at'])).total_seconds()
            if age>policy.loss_window_seconds or trade['pnl']>=0:break
            streak+=1
            if streak>=policy.loss_streak_limit:return 'loss_streak'
    return None

def performance(trades):
    pnls=[t['pnl'] for t in trades];wins=[p for p in pnls if p>0];losses=[p for p in pnls if p<0]
    streak=maximum=0
    for pnl in pnls:
        streak=streak+1 if pnl<0 else 0;maximum=max(maximum,streak)
    average_win=sum(wins)/len(wins) if wins else None
    average_loss=-sum(losses)/len(losses) if losses else None
    return dict(expectancy_per_closed_trade=round(sum(pnls)/len(pnls),4) if pnls else None,
        average_win=round(average_win,4) if average_win is not None else None,
        average_loss=round(average_loss,4) if average_loss is not None else None,
        payoff_ratio=round(average_win/average_loss,4) if average_win is not None and average_loss else None,
        current_loss_streak=streak,max_loss_streak=maximum)
