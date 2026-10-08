"""Conservative next-bar-open fills; no future candles used for signal generation."""
from .models import Instrument, Market, Portfolio
from .risk import RiskEngine
from .paper import PaperBroker
from .strategy import sma_signal,Signal

def backtest(rows, symbol="ASSET", market="crypto", initial_cash=10000):
    if len(rows)<30: raise ValueError("Need 30+ rows")
    broker=PaperBroker(Portfolio(cash=initial_cash,equity_at_day_start=initial_cash),RiskEngine())
    instrument=Instrument(symbol,Market(market))
    equity_curve=[]
    for i in range(21,len(rows)):
        price=rows[i]["open"]
        marks={symbol:price}
        broker.apply_stops(marks)
        signal=sma_signal([r["close"] for r in rows[:i]])
        if signal==Signal.BUY: broker.buy(instrument,price,marks)
        elif signal==Signal.SELL: broker.sell(symbol,price)
        equity_curve.append(broker.equity({symbol:rows[i]["close"]}))
    final=broker.equity({symbol:rows[-1]["close"]})
    peak=initial_cash
    drawdown=0.0
    for e in equity_curve:
        peak=max(peak,e)
        drawdown=max(drawdown,(peak-e)/peak)
    return {"initial_equity":initial_cash,"final_equity":round(final,2),"return_pct":round((final/initial_cash-1)*100,3),"max_drawdown_pct":round(drawdown*100,3),"fills":len(broker.fills),"closed_trade_pnl":round(broker.portfolio.realized_pnl,2),"open_positions":len(broker.portfolio.positions)}
