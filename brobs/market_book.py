"""Separate durable, unleveraged stock/USD and crypto/USDT paper ledgers."""
import math
from .fx import FXBook,FXConfig

STOCKS=('AAPL','MSFT','NVDA','SPY')
CRYPTO=('BTC_USDT','ETH_USDT')

class StockBook(FXBook):
    profile='stock'
    quote_currency='USD'
    allowed_symbols=STOCKS
    def permits_short(self,symbol):return False

class CryptoBook(FXBook):
    profile='crypto'
    quote_currency='USDT'
    allowed_symbols=CRYPTO
    def permits_short(self,symbol):return False
    def quantize_units(self,units):return math.floor(units*1000000)/1000000


def default_config(market):
    if market=='forex':return FXConfig()
    if market not in ('stock','crypto'):raise ValueError('Unknown market')
    return FXConfig(stop_fraction=.02,reward_risk=2,commission_fraction=.001 if market=='crypto' else 0,
        slippage_fraction=.0005,max_spread_fraction=.005)

BOOKS={'forex':FXBook,'stock':StockBook,'crypto':CryptoBook}
