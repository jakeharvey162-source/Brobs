"""Paper-only long spot simulator. No broker credentials and no live orders."""
from dataclasses import dataclass
from math import isfinite
from .models import Portfolio, Instrument
from .risk import RiskEngine

@dataclass
class Fill:
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float

class PaperBroker:
    def __init__(self, portfolio: Portfolio, risk: RiskEngine, fee_fraction: float = 0.001, slippage_fraction: float = 0.0005):
        if any(not isfinite(v) or v < 0 or v >= 1 for v in (fee_fraction, slippage_fraction)):
            raise ValueError("Invalid cost parameter")
        self.portfolio, self.risk = portfolio, risk
        self.fee_fraction, self.slippage_fraction = fee_fraction, slippage_fraction
        self.fills: list[Fill] = []

    def equity(self, prices: dict[str, float]) -> float:
        value = self.portfolio.cash
        for symbol, position in self.portfolio.positions.items():
            if symbol not in prices or not isfinite(prices[symbol]) or prices[symbol] <= 0:
                raise ValueError("Missing or invalid mark price: " + symbol)
            value += position["quantity"] * prices[symbol]
        return value

    def buy(self, instrument: Instrument, price: float, prices: dict[str, float]) -> Fill | None:
        if not isfinite(price) or price <= 0 or instrument.symbol in self.portfolio.positions:
            return None
        marked = self.equity(prices)
        if self.risk.check_halt(self.portfolio, marked):
            return None
        effective_price = price * (1 + self.slippage_fraction)
        qty = self.risk.quantity(marked, self.portfolio.cash / (1 + self.fee_fraction), effective_price)
        cost = qty * effective_price
        fee = cost * self.fee_fraction
        if qty <= 0 or cost + fee > self.portfolio.cash + 1e-8:
            return None
        self.portfolio.cash -= cost + fee
        self.portfolio.positions[instrument.symbol] = {"quantity": qty, "entry": effective_price, "entry_fee": fee, "stop": effective_price * (1 - self.risk.config.stop_distance_fraction)}
        fill = Fill(instrument.symbol, "buy", qty, effective_price, fee)
        self.fills.append(fill)
        return fill

    def sell(self, symbol: str, price: float) -> Fill | None:
        position = self.portfolio.positions.get(symbol)
        if position is None or not isfinite(price) or price <= 0:
            return None
        effective_price = price * (1 - self.slippage_fraction)
        qty = position["quantity"]
        proceeds = qty * effective_price
        fee = proceeds * self.fee_fraction
        self.portfolio.cash += proceeds - fee
        self.portfolio.realized_pnl += proceeds - fee - qty * position["entry"] - position["entry_fee"]
        del self.portfolio.positions[symbol]
        fill = Fill(symbol, "sell", qty, effective_price, fee)
        self.fills.append(fill)
        return fill

    def apply_stops(self, prices: dict[str, float]) -> list[Fill]:
        # Reject invalid or incomplete snapshots before mutating positions.
        self.equity(prices)
        closed = []
        for symbol, position in list(self.portfolio.positions.items()):
            price = prices.get(symbol)
            if price is not None and price <= position["stop"]:
                fill = self.sell(symbol, price)
                if fill: closed.append(fill)
        self.risk.check_halt(self.portfolio, self.equity(prices))
        return closed
