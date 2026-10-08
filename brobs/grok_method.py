"""Free, independently implemented multi-timeframe research; not a Grok model."""
from statistics import mean
from math import isfinite
from datetime import timedelta
from .fx import utc
from .market_signals import rsi

def ema(values, period):
    value=values[0];alpha=2/(period+1)
    for price in values[1:]:value+=alpha*(price-value)
    return value

def complete_four_hour_closes(rows):
    """Only four consecutive UTC-aligned hourly bars; drop partial buckets."""
    buckets={}
    for row in rows:
        at=utc(row['timestamp'])
        if at.minute or at.second or at.microsecond:raise ValueError('Hourly UTC bars required')
        start=at.replace(hour=at.hour//4*4)
        buckets.setdefault(start,[]).append(row)
    return [part[-1]['close'] for start,part in sorted(buckets.items())
            if len(part)==4 and all(utc(r['timestamp'])==start+timedelta(hours=i) for i,r in enumerate(part))]

def consensus(rows,side=0,threshold=20,allow_short=False):
    from .market_data import validate_bars
    if not isfinite(threshold) or not 0<threshold<50:raise ValueError('Invalid recovery threshold')
    rows=validate_bars(rows)
    if len(rows)<100:return 'hold',[dict(agent='data_quality',action='veto',reason='Need 100 completed hourly OHLC bars')]
    if any((utc(b['timestamp'])-utc(a['timestamp'])).total_seconds()!=3600 for a,b in zip(rows[-24:],rows[-23:])):
        return 'hold',[dict(agent='data_quality',action='veto',reason='Recent hourly gaps or non-hourly bars')]
    higher=complete_four_hour_closes(rows)
    if len(higher)<20:return 'hold',[dict(agent='data_quality',action='veto',reason='Need 20 complete UTC four-hour bars')]
    closes=[r['close'] for r in rows];last=closes[-1];trend=ema(closes,50)
    upper=ema(higher,20);strength=rsi(closes,2);previous=rsi(closes[:-1],2)
    ranges=[max(r['high']-r['low'],abs(r['high']-p['close']),abs(r['low']-p['close'])) for p,r in zip(rows[-15:-1],rows[-14:])]
    atr=mean(ranges)/last;safe=isfinite(atr) and atr<=.02
    up=last>trend and higher[-1]>upper;down=last<trend and higher[-1]<upper
    action='hold'
    if side>0 and (strength>=70 or last<trend):action='close'
    elif side<0 and (strength<=30 or last>trend):action='close'
    elif not side and safe:
        if up and previous<threshold<=strength:action='buy'
        elif allow_short and down and previous>100-threshold>=strength:action='sell'
    votes=[dict(agent='multi_timeframe',action='buy' if up else 'sell' if down else 'hold',reason='Hourly EMA50 and complete UTC 4h EMA20 must agree'),
           dict(agent='pullback_recovery',action=action,reason=f'RSI2 {previous:.2f} to {strength:.2f}; recovery threshold {threshold}'),
           dict(agent='volatility',action='permit' if safe else 'veto',reason=f'ATR14 / close {atr:.6f}; maximum 0.02'),
           dict(agent='information',action='unknown',reason='No verified news, sentiment or funding feed; none inferred')]
    return action,votes
