from dataclasses import dataclass
from math import isfinite, floor
from .models import Portfolio

@dataclass(frozen=True)
class RiskConfig:
    max_risk_fraction: float = 0.005
    max_daily_loss_fraction: float = 0.02
    max_position_fraction: float = 0.10
    stop_distance_fraction: float = 0.02

    def __post_init__(self):
        for value in (self.max_risk_fraction, self.max_daily_loss_fraction, self.max_position_fraction, self.stop_distance_fraction):
            if not isfinite(value) or not 0 < value < 1:
                raise ValueError("Risk fractions must be between zero and one")

class RiskEngine:
    def __init__(self, config: RiskConfig = RiskConfig()):
        self.config = config

    def check_halt(self, portfolio: Portfolio, marked_equity: float) -> bool:
        if portfolio.equity_at_day_start <= 0 or not isfinite(marked_equity):
            portfolio.halted = True
        elif marked_equity <= portfolio.equity_at_day_start * (1 - self.config.max_daily_loss_fraction):
            portfolio.halted = True
        return portfolio.halted

    def quantity(self, equity: float, cash: float, price: float) -> float:
        if not all(isfinite(x) and x > 0 for x in (equity, cash, price)):
            return 0.0
        risk_budget = equity * self.config.max_risk_fraction
        by_stop = risk_budget / (price * self.config.stop_distance_fraction)
        by_cap = equity * self.config.max_position_fraction / price
        by_cash = cash / price
        return max(0.0, min(by_stop, by_cap, by_cash))
