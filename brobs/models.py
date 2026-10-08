from dataclasses import dataclass, field
from enum import Enum

class Market(str, Enum):
    CRYPTO = "crypto"
    FOREX = "forex"
    STOCK = "stock"

@dataclass(frozen=True)
class Instrument:
    symbol: str
    market: Market

@dataclass(frozen=True)
class Candle:
    close: float

@dataclass
class Portfolio:
    cash: float = 10000.0
    equity_at_day_start: float = 10000.0
    realized_pnl: float = 0.0
    halted: bool = False
    positions: dict = field(default_factory=dict)
