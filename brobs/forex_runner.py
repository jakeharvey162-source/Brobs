"""One-shot OANDA practice-data research runner. No Forex orders or simulated FX fills.

Generic spot simulator cannot account correctly for FX margin, currency conversion or swaps.
Fail closed: record signals and positions without placing any trade.
"""
import argparse,json
from .oanda_practice import PracticeData
from .ledger import PaperLedger
from .agents import Coordinator
from .paper import PaperBroker
from .risk import RiskEngine

def run_once(data,ledger,instrument="EUR_USD"):
    candles=data.candles(instrument=instrument)
    last=candles[-1]
    event_id=instrument+":"+last["timestamp"].isoformat()
    price=last["close"]
    if not 0<price<1e12:raise ValueError("Invalid last price")
    def evaluate(portfolio):
        # Prior generic FX buy/sell simulation was misleading; require FX-specific
        # contract, quote-currency conversion and margin engine before enabling fills.
        marks={s:p["entry"] for s,p in portfolio.positions.items()}
        marks[instrument]=price
        broker=PaperBroker(portfolio,RiskEngine())
        equity=broker.equity(marks)
        decision,votes=Coordinator().decide([c["close"] for c in candles],portfolio,equity)
        return {"status":"research_only","event_id":event_id,"symbol":instrument,
                "price":price,"decision":decision,"votes":[vars(v) for v in votes],
                "fills":[],"cash":portfolio.cash,"equity":equity,
                "reason":"FX orders disabled pending correct margin, spread and currency conversion accounting"}
    result=ledger.process_once(event_id,evaluate)
    return result if result is not None else {"status":"duplicate_candle","event_id":event_id}

def main():
    p=argparse.ArgumentParser();p.add_argument("--db",default="brobs_paper.db");p.add_argument("--pair",default="EUR_USD");a=p.parse_args()
    print(json.dumps(run_once(PracticeData(),PaperLedger(a.db),a.pair),indent=2))
if __name__=="__main__":main()
