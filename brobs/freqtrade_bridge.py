"""Independent vectorized BROBS trend signals for optional Freqtrade integration."""
import math

def columns(frame):
    df=frame.copy()
    close=df['close']
    valid=close.map(lambda v:not isinstance(v,bool) and isinstance(v,(int,float)) and math.isfinite(v) and v>0)
    safe=close.where(valid)
    fast=safe.rolling(8).mean();slow=safe.rolling(21).mean()
    momentum=safe/safe.shift(5)-1
    vol=(safe/safe.shift(1)-1).rolling(20).std(ddof=0)
    threshold=(vol*.5).clip(lower=.0002)
    ready=valid.rolling(30).sum().eq(30)&vol.le(.015)
    df['brobs_buy']=ready&fast.gt(slow*1.0001)&momentum.gt(threshold)
    df['brobs_sell']=ready&fast.lt(slow*.9999)&momentum.lt(-threshold)
    return df

def stake_cap(equity,rate,proposed,min_stake,max_stake):
    values=[equity,rate,proposed,max_stake]+([] if min_stake is None else [min_stake])
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0 for v in values) or equity<=0 or rate<=0:return 0
    # 0.5% equity stop-risk budget, 2% stop, 20% full-notional cap.
    stake=min(proposed,max_stake,equity*.2,equity*.005/(.02+.002+.001))
    return stake if stake>0 and (min_stake is None or stake>=min_stake) else 0
