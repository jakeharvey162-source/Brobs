"""Independent standard indicator strategies, strictly past/closed OHLC bars."""
from math import isfinite
from statistics import mean
from .fx_signals import decide

FAMILIES=('trend','rsi_pullback','rsi2_reversion','donchian','grok_consensus')

def rsi(closes,period=14):
    if period<2 or len(closes)<=period:return None
    changes=[b-a for a,b in zip(closes,closes[1:])]
    gain=mean(max(v,0) for v in changes[:period]);loss=mean(max(-v,0) for v in changes[:period])
    for value in changes[period:]:
        gain=(gain*(period-1)+max(value,0))/period;loss=(loss*(period-1)+max(-value,0))/period
    if loss==0:return 100.0 if gain else 50.0
    return 100-100/(1+gain/loss)

def signal(rows,family='trend',side=0,threshold=None,allow_short=False):
    if family not in FAMILIES:raise ValueError('Unknown strategy family')
    threshold=(40 if family=='rsi_pullback' else 20 if family=='grok_consensus' else 10) if threshold is None else threshold
    if not isfinite(threshold) or not 0 < threshold < 50:raise ValueError('Invalid RSI threshold')
    closes=[r['close'] for r in rows]
    if len(closes)<100 or any(not isfinite(c) or c<=0 for c in closes):
        return 'hold',[dict(agent='data_quality',action='veto',reason='Need 100+ valid completed prices')]
    if family=='trend':return decide(closes)
    if family=='grok_consensus':
        from .grok_method import consensus
        return consensus(rows,side,threshold,allow_short)
    last=closes[-1];regime=mean(closes[-100:]);fast=mean(closes[-5:]);strength=rsi(closes,2 if family=='rsi2_reversion' else 14)
    action='hold'
    if family=='rsi2_reversion':
        if side>0 and (last>=fast or strength>=70):action='close'
        elif side<0 and (last<=fast or strength<=30):action='close'
        elif not side:
            if last>regime and strength<threshold:action='buy'
            elif allow_short and last<regime and strength>100-threshold:action='sell'
    elif family=='rsi_pullback':
        if side>0 and (strength>=65 or last<regime):action='close'
        elif side<0 and (strength<=35 or last>regime):action='close'
        elif not side:
            if last>regime and strength<threshold:action='buy'
            elif allow_short and last<regime and strength>100-threshold:action='sell'
    elif family=='donchian':
        upper=max(r['high'] for r in rows[-21:-1]);lower=min(r['low'] for r in rows[-21:-1])
        exit_long=min(r['low'] for r in rows[-11:-1]);exit_short=max(r['high'] for r in rows[-11:-1])
        if side>0 and last<exit_long:action='close'
        elif side<0 and last>exit_short:action='close'
        elif not side:
            if last>upper and last>regime:action='buy'
            elif allow_short and last<lower and last<regime:action='sell'
    return action,[dict(agent=family,action=action,reason=f'Closed-bar RSI {strength:.2f}, SMA100 {regime:.6f}; experimental, not a win probability')]
