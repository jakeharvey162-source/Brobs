"""TradingView-compatible paper-only webhook gateway. NEVER sends live orders."""
import hmac,json,os
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from .models import Instrument,Market,Portfolio
from .risk import RiskEngine
from .paper import PaperBroker

class PaperAlertService:
    def __init__(self,token,pause_file=None):
        if not token or len(token)<24: raise ValueError("Configure a random secret with at least 24 characters")
        self.token=token
        self.pause_file=pause_file if pause_file is not None else os.environ.get('BROBS_ALERT_PAUSE_FILE')
        self.broker=PaperBroker(Portfolio(),RiskEngine())
        self.seen=set()
    def handle(self,payload):
        if not isinstance(payload,dict): raise ValueError("JSON object required")
        if not hmac.compare_digest(str(payload.get("secret","")),self.token): raise PermissionError("Unauthorized")
        event_id=payload.get("event_id")
        if not isinstance(event_id,str) or not 1<=len(event_id)<=128: raise ValueError("event_id required")
        if event_id in self.seen:return {"status":"duplicate"}
        symbol=payload.get("symbol")
        if not isinstance(symbol,str) or not 1<=len(symbol)<=32 or not all(c.isalnum() or c in "-_./" for c in symbol): raise ValueError("Invalid symbol")
        market=Market(payload.get("market"))
        if market==Market.FOREX:raise ValueError("Forex alerts require verified bid/ask quotes through the FX runner")
        action=payload.get("action")
        if action not in ("buy","sell","hold"): raise ValueError("Invalid action")
        # Local operator kill switch: no new paper entries, but exits still permitted.
        # Mark the alert as consumed so a stale buy cannot be replayed on resume.
        if action=="buy" and self.pause_file and os.path.exists(self.pause_file):
            self.seen.add(event_id)
            return {"status":"paper_entries_paused","action":action,"symbol":symbol,"cash":round(self.broker.portfolio.cash,2)}

        price=float(payload.get("price",0))
        if not 0<price<1e12:raise ValueError("Invalid price")
        if action=="buy": fill=self.broker.buy(Instrument(symbol,market),price,{symbol:price,**{s:p["entry"] for s,p in self.broker.portfolio.positions.items()}})
        elif action=="sell":fill=self.broker.sell(symbol,price)
        else:fill=None
        self.seen.add(event_id)
        return {"status":"paper_filled" if fill else "paper_no_action","action":action,"symbol":symbol,"cash":round(self.broker.portfolio.cash,2)}

def serve(port=8766):
    token=os.environ.get("BROBS_ALERT_SECRET","")
    service=PaperAlertService(token)
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path!="/alert":self.send_error(404);return
            try:length=int(self.headers.get("Content-Length","0"))
            except ValueError:self.send_error(400);return
            if not 0<length<=4096:self.send_error(413);return
            try:
                payload=json.loads(self.rfile.read(length))
                result=service.handle(payload)
                status=200
            except PermissionError:result={"error":"unauthorized"};status=401
            except (ValueError,TypeError,KeyError,json.JSONDecodeError):result={"error":"invalid_request"};status=400
            body=json.dumps(result).encode()
            self.send_response(status);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    print("BROBS paper webhook listening on 127.0.0.1:"+str(port))
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()

if __name__=="__main__":serve()
