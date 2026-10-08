"""Independent research agents. No live order submission."""
from dataclasses import dataclass
from statistics import mean, pstdev
from math import isfinite
from .strategy import sma_signal, Signal
from .risk import RiskEngine, RiskConfig

@dataclass(frozen=True)
class Vote:
    agent: str
    action: str
    confidence: float
    reason: str

class TrendAgent:
    name = "trend"
    def evaluate(self, closes):
        signal = sma_signal(closes)
        return Vote(self.name, signal.value, 0.55 if signal != Signal.HOLD else 0.0, "SMA crossover")

class MomentumAgent:
    name = "momentum"
    def evaluate(self, closes):
        if len(closes) < 15 or any(not isfinite(x) or x <= 0 for x in closes):
            return Vote(self.name, "hold", 0, "Insufficient or invalid prices")
        recent = closes[-1] / closes[-6] - 1
        previous = closes[-6] / closes[-11] - 1
        action = "buy" if recent > 0.015 and previous > 0 else "sell" if recent < -0.015 and previous < 0 else "hold"
        return Vote(self.name, action, min(0.7, abs(recent) * 5) if action != "hold" else 0, "Two-window momentum")

class VolatilityAgent:
    name = "volatility"
    def evaluate(self, closes):
        if len(closes) < 22 or any(not isfinite(x) or x <= 0 for x in closes):
            return Vote(self.name, "veto", 1, "Insufficient or invalid prices")
        returns = [closes[i] / closes[i-1] - 1 for i in range(len(closes)-20, len(closes))]
        vol = pstdev(returns)
        return Vote(self.name, "veto" if vol > 0.06 else "clear", 1, f"Daily-bar return volatility {vol:.3f}")

class InformationAgent:
    name = "information"
    def evaluate(self, context):
        # External news feeds must be verified and timestamped; missing context abstains.
        if not context or not context.get("verified") or not context.get("timestamp"):
            return Vote(self.name, "unknown", 0, "No verified timestamped news feed")
        return Vote(self.name, "clear", 0, "Verified feed present; no sentiment model connected")

class RiskAgent:
    name = "risk"
    def __init__(self, config=None): self.engine = RiskEngine(config or RiskConfig())
    def evaluate(self, portfolio, equity):
        return Vote(self.name, "veto" if self.engine.check_halt(portfolio, equity) else "clear", 1, "Portfolio daily-loss circuit breaker")

class Coordinator:
    """Requires agreement between trend and momentum; vetoes override signals."""
    def __init__(self):
        self.trend = TrendAgent()
        self.momentum = MomentumAgent()
        self.volatility = VolatilityAgent()
        self.information = InformationAgent()
        self.risk = RiskAgent()

    def decide(self, closes, portfolio, equity, context=None):
        votes = [self.trend.evaluate(closes), self.momentum.evaluate(closes), self.volatility.evaluate(closes), self.information.evaluate(context), self.risk.evaluate(portfolio, equity)]
        if any(v.action == "veto" for v in votes): return "hold", votes
        directional = [v.action for v in votes[:2]]
        if directional[0] == directional[1] and directional[0] in ("buy", "sell"):
            return directional[0], votes
        return "hold", votes
