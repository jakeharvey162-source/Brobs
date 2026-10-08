"""Experimental closed-bar mean reversion, not a calibrated win probability."""
from math import isfinite
from statistics import mean, pstdev


def reversion(closes, period=20, deviation=2.0):
    if period < 10 or not 1 <= deviation <= 3:
        raise ValueError('Invalid reversion parameters')
    if len(closes) < period or any(not isfinite(p) or p <= 0 for p in closes):
        return 'hold', [dict(agent='data_quality', action='veto', reason='Invalid or insufficient prices')]
    window=closes[-period:]
    center=mean(window); scale=pstdev(window)
    z=(window[-1]-center)/scale if scale else 0
    action='buy' if z <= -deviation else 'sell' if z >= deviation else 'hold'
    return action, [dict(agent='mean_reversion',action=action,reason=f'{period}-bar price deviation {z:.3f} standard deviations')]
