"""One-shot forex practice-data runner with LOCAL simulated execution only."""
import argparse,json,os,uuid
from datetime import datetime,timezone
from .oanda_practice import PracticeData
from .ledger import PaperLedger
from .agents import Coordinator
from .paper import PaperBroker
from .risk import RiskEngine
from .models import Instrument,Market

def run_once(data,ledger,instrument="EUR_USD"):
    candles=data.candles(instrument=instrument)
    last=candles[-1]
    event_id=instrument+":"+last["timestamp"].isoformat()
    # Repeated candle is not processed again. All writes are committed to local SQLite.
    if any(e["event_id"]==event_id for e in ledger.recent(100)):return {"status":"duplicate_candle","event_id":event_id}
    portfolio=ledger.load()
    broker=PaperBroker(portfolio,RiskEngine())
    price=last["close"]
    marks={s:p["entry"] for s,p in portfolio.positions.items()};marks[instrument]=price
    broker.apply_stops(marks)
    decision,votes=Coordinator().decide([c["close"] for c in candles],portfolio,broker.equity(marks))
    if decision=="buy":broker.buy(Instrument(instrument,Market.FOREX),price,marks)
    elif decision=="sell":broker.sell(instrument,price)
    result={"status":"paper_only","event_id":event_id,"symbol":instrument,"price":price,"decision":decision,"votes":[vars(v) for v in votes],"fills":[vars(f) for f in broker.fills],"cash":portfolio.cash,"equity":broker.equity(marks)}
    if not ledger.save(portfolio,event_id,result):return {"status":"duplicate_candle","event_id":event_id}
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument("--db",default="brobs_paper.db");p.add_argument("--pair",default="EUR_USD");a=p.parse_args()
    result=run_once(PracticeData(),PaperLedger(a.db),a.pair)
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
