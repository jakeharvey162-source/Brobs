"""Read-only localhost dashboard backed by persistent SQLite paper ledger."""
import argparse,json,html
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from .ledger import PaperLedger

def serve(db_path,port=8767):
    ledger=PaperLedger(db_path)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ("/","/api/state"):self.send_error(404);return
            p=ledger.load();state={"mode":"LOCAL PAPER ONLY","cash":p.cash,"realized_pnl":p.realized_pnl,"halted":p.halted,"positions":p.positions,"events":ledger.recent(25)}
            if self.path=="/api/state":
                body=json.dumps(state).encode();mime="application/json"
            else:
                safe=html.escape(json.dumps(state,indent=2))
                body=("<!doctype html><html><head><meta name='viewport' content='width=device-width'><title>BROBS Forex</title><style>body{background:#091421;color:#e4fff5;font:16px system-ui;max-width:1000px;margin:40px auto;padding:20px}h1{color:#62e5aa}pre{white-space:pre-wrap;background:#132638;padding:20px;border-radius:12px}small{color:#9fb8b1}</style></head><body><h1>BROBS AI / Forex Paper Dashboard</h1><small>Local simulation only — no OANDA orders or real-money trading</small><pre>"+safe+"</pre></body></html>").encode();mime="text/html; charset=utf-8"
            self.send_response(200);self.send_header("Content-Type",mime);self.send_header("Cache-Control","no-store");self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)
    print("Open http://127.0.0.1:"+str(port))
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--db",default="brobs_paper.db");p.add_argument("--port",type=int,default=8767);a=p.parse_args();serve(a.db,a.port)
