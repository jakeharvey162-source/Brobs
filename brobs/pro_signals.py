"""Independent closed-bar indicator families with an explicit cost hurdle."""
from statistics import mean,pstdev
from math import isfinite
from .market_signals import rsi

FAMILIES=('band_recovery','range_reversion','macd_swing')

def features(rows):
    closes=[r['close'] for r in rows]
    if len(rows)<200 or any(not isfinite(v) or v<=0 for v in closes):return None
    averages={p:closes[0] for p in (12,26,50,200)};signal_line=0;previous_hist=0
    for price in closes:
        previous_hist=(averages[12]-averages[26])-signal_line
        for p in averages:averages[p]+=(price-averages[p])*2/(p+1)
        macd=averages[12]-averages[26];signal_line+=(macd-signal_line)*2/10
    center=mean(closes[-20:]);scale=pstdev(closes[-20:]);previous_center=mean(closes[-21:-1]);previous_scale=pstdev(closes[-21:-1])
    travel=sum(abs(b-a) for a,b in zip(closes[-21:-1],closes[-20:]))
    efficiency=abs(closes[-1]-closes[-21])/travel if travel else 0
    return dict(last=closes[-1],previous=closes[-2],center=center,scale=scale,previous_center=previous_center,
        previous_scale=previous_scale,rsi=rsi(closes),ema50=averages[50],ema200=averages[200],
        histogram=macd-signal_line,previous_histogram=previous_hist,efficiency=efficiency)

def decision(f,family,side=0,threshold=40,allow_short=False,roundtrip_cost=.0035):
    if family not in FAMILIES or not 0<threshold<50 or not 0<=roundtrip_cost<.1:raise ValueError('Invalid strategy parameters')
    if f is None:return 'hold',[dict(agent='data_quality',action='veto',reason='Need 200 valid completed closes')]
    last=f['last'];strength=f['rsi'];up=last>f['ema200'];down=last<f['ema200'];action='hold'
    long_hurdle=(f['center']-last)/last>=2*roundtrip_cost
    short_hurdle=(last-f['center'])/last>=2*roundtrip_cost
    if family=='macd_swing':
        if side>0 and (f['histogram']<0 or not up):action='close'
        elif side<0 and (f['histogram']>0 or not down):action='close'
        elif not side:
            if up and f['histogram']>0>=f['previous_histogram'] and 45<=strength<=70:action='buy'
            elif allow_short and down and f['histogram']<0<=f['previous_histogram'] and 30<=strength<=55:action='sell'
    else:
        if side>0 and (last>=f['center'] or strength>=65):action='close'
        elif side<0 and (last<=f['center'] or strength<=35):action='close'
        elif not side:
            lower=f['center']-2*f['scale'];upper=f['center']+2*f['scale']
            if family=='band_recovery':
                long_setup=f['previous']<f['previous_center']-2*f['previous_scale'] and last>=lower and up
                short_setup=f['previous']>f['previous_center']+2*f['previous_scale'] and last<=upper and down
            else:
                long_setup=last<lower and f['efficiency']<.3
                short_setup=last>upper and f['efficiency']<.3
            if long_setup and strength<threshold and long_hurdle:action='buy'
            elif allow_short and short_setup and strength>100-threshold and short_hurdle:action='sell'
    return action,[dict(agent=family,action=action,reason=f'RSI14 {strength:.2f}; efficiency {f["efficiency"]:.3f}; EMA200 regime; closed bars only'),
                   dict(agent='cost_hurdle',action='permit' if family=='macd_swing' or side or long_hurdle or short_hurdle else 'veto',reason=f'Band entries need mean-return distance >= twice estimated roundtrip cost {roundtrip_cost:.6f}; not a price forecast')]

def signal(rows,family,side=0,threshold=40,allow_short=False,roundtrip_cost=.0035):
    return decision(features(rows),family,side,threshold,allow_short,roundtrip_cost)

class FeatureCache:
    """Every feature uses the same previous-500-bar window as the runner."""
    def __init__(self,rows):
        self.values={r['timestamp']:features(rows[max(0,i-499):i+1]) for i,r in enumerate(rows)}
    def callback(self,family,threshold,allow_short,cost):
        return lambda history,side:decision(self.values[history[-1]['timestamp']],family,side,threshold,allow_short,cost)
