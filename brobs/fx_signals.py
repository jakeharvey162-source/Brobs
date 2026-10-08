"""Forex-scale research votes. Confidence is not a calibrated win probability."""
from math import isfinite
from statistics import mean, pstdev

def decide(closes, use_ml=False):
    if len(closes) < 30 or any(not isfinite(p) or p <= 0 for p in closes):
        return 'hold', [{'agent':'data_quality','action':'veto','reason':'Need 30+ finite positive prices'}]
    fast, slow = mean(closes[-8:]), mean(closes[-21:])
    momentum = closes[-1]/closes[-6]-1
    returns = [closes[i]/closes[i-1]-1 for i in range(len(closes)-20, len(closes))]
    volatility = pstdev(returns)
    trend = 'buy' if fast > slow*1.0001 else 'sell' if fast < slow*.9999 else 'hold'
    threshold = max(.0002, volatility*.5)
    motion = 'buy' if momentum > threshold else 'sell' if momentum < -threshold else 'hold'
    veto = volatility > .015
    votes = [dict(agent='trend', action=trend, reason='8/21-bar moving-average regime'),
        dict(agent='momentum', action=motion, reason='Five-bar move above volatility-scaled threshold'),
        dict(agent='volatility', action='veto' if veto else 'clear', reason=f'Bar-return volatility {volatility:.6f}'),
        dict(agent='information', action='unknown', reason='No verified economic-calendar/news feed; no fabricated sentiment')]
    action = trend if trend == motion and not veto else 'hold'
    if use_ml:
        from .ml_agent import predict
        model_vote = predict(closes)
        votes.append(model_vote)
        # Unvalidated/absent models abstain; a measured contrary vote vetoes entry.
        if model_vote['action'] in ('buy','sell') and model_vote['action'] != action:
            action = 'hold'
    return action, votes
