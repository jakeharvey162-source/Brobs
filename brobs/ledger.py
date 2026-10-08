"""SQLite paper portfolio ledger: persistent snapshots and deduplicated events."""
import json,sqlite3
from pathlib import Path
from .models import Portfolio

class PaperLedger:
    def __init__(self,path):
        self.path=str(path)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS portfolio (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, data TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    def connect(self):return sqlite3.connect(self.path,timeout=10)
    def load(self):
        with self.connect() as db:row=db.execute("SELECT data FROM portfolio WHERE id=1").fetchone()
        if not row:return Portfolio()
        d=json.loads(row[0]);return Portfolio(cash=d["cash"],equity_at_day_start=d["equity_at_day_start"],realized_pnl=d["realized_pnl"],halted=d["halted"],positions=d["positions"])
    def save(self,portfolio,event_id,payload):
        state={k:getattr(portfolio,k) for k in ("cash","equity_at_day_start","realized_pnl","halted","positions")}
        with self.connect() as db:
            if db.execute("SELECT 1 FROM events WHERE event_id=?",(event_id,)).fetchone():return False
            db.execute("INSERT INTO events(event_id,data) VALUES (?,?)",(event_id,json.dumps(payload)))
            db.execute("INSERT INTO portfolio(id,data) VALUES (1,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",(json.dumps(state),))
            return True
    def recent(self,limit=30):
        with self.connect() as db:
            return [{"event_id":r[0],"data":json.loads(r[1]),"created_at":r[2]} for r in db.execute("SELECT event_id,data,created_at FROM events ORDER BY created_at DESC,rowid DESC LIMIT ?",(max(1,min(limit,100)),))]
