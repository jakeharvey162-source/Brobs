"""Illustrative SMA crossover signal, not a recommendation."""
from enum import Enum
from math import isfinite

class Signal(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

def sma_signal(closes: list[float], short: int = 5, long: int = 20) -> Signal:
    if not 1 <= short < long:
        raise ValueError("Require 1 <= short < long")
    if len(closes) < long + 1 or any(not isfinite(p) or p <= 0 for p in closes):
        return Signal.HOLD
    prev_fast = sum(closes[-short-1:-1]) / short
    prev_slow = sum(closes[-long-1:-1]) / long
    fast = sum(closes[-short:]) / short
    slow = sum(closes[-long:]) / long
    if prev_fast <= prev_slow and fast > slow:
        return Signal.BUY
    if prev_fast >= prev_slow and fast < slow:
        return Signal.SELL
    return Signal.HOLD
