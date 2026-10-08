"""Synthetic data demonstration only: not real market performance."""
from .models import Portfolio, Instrument, Market
from .risk import RiskEngine
from .paper import PaperBroker
from .strategy import sma_signal, Signal

def main():
    instrument = Instrument("DEMO-USD", Market.CRYPTO)
    broker = PaperBroker(Portfolio(), RiskEngine())
    series = [100.0] * 25 + [100.0 + i for i in range(1, 10)] + [109.0 - i for i in range(1, 12)]
    for index in range(21, len(series)):
        price = series[index]
        mark = {instrument.symbol: price}
        broker.apply_stops(mark)
        signal = sma_signal(series[: index + 1])
        if signal == Signal.BUY: broker.buy(instrument, price, mark)
        if signal == Signal.SELL: broker.sell(instrument.symbol, price)
    print("BROBS AI | SYNTHETIC PAPER DEMO (not real performance)")
    print("Fills:", len(broker.fills), "| Realized P/L:", round(broker.portfolio.realized_pnl, 2))
    print("Final marked equity:", round(broker.equity({instrument.symbol: series[-1]}), 2))

if __name__ == "__main__": main()
