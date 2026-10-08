"""Durable SQLite ledger with serialized, atomic paper decisions."""
import json
import sqlite3
from .models import Portfolio

class PaperLedger:
    def __init__(self,path):
        self.path=str(path)
        with self.connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS portfolio (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL)")
            db.execute("CREATE TABLE IF NOT EXISTS events (event_id TEXT PRIMARY KEY, data TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    def connect(self):
        return sqlite3.connect(self.path,timeout=15)
    @staticmethod
    def _deserialize(row):
        if not row:return Portfolio()
        d=json.loads(row[0])
        return Portfolio(cash=d["cash"],equity_at_day_start=d["equity_at_day_start"],realized_pnl=d["realized_pnl"],halted=d["halted"],positions=d["positions"])
    @staticmethod
    def _serialize(p):
        return json.dumps({k:getattr(p,k) for k in ("cash","equity_at_day_start","realized_pnl","halted","positions")},allow_nan=False)
    def load(self):
        with self.connect() as db:return self._deserialize(db.execute("SELECT data FROM portfolio WHERE id=1").fetchone())
    def has_event(self,event_id):
        with self.connect() as db:return db.execute("SELECT 1 FROM events WHERE event_id=?",(event_id,)).fetchone() is not None
    def save(self,portfolio,event_id,payload):
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM events WHERE event_id=?",(event_id,)).fetchone():return False
            db.execute("INSERT INTO events(event_id,data) VALUES (?,?)",(event_id,json.dumps(payload,allow_nan=False)))
            db.execute("INSERT INTO portfolio(id,data) VALUES (1,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",(self._serialize(portfolio),))
            return True
    def process_once(self,event_id,callback):
        """Serialize concurrent workers, read latest state, calculate, and commit together.

        Callback accepts Portfolio and returns JSON-serializable event payload.
        Exceptions roll back the entire transaction.
        """
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM events WHERE event_id=?",(event_id,)).fetchone():return None
            p=self._deserialize(db.execute("SELECT data FROM portfolio WHERE id=1").fetchone())
            payload=callback(p)
            encoded=json.dumps(payload,allow_nan=False)
            state=self._serialize(p)
            db.execute("INSERT INTO events(event_id,data) VALUES (?,?)",(event_id,encoded))
            db.execute("INSERT INTO portfolio(id,data) VALUES (1,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data",(state,))
            return payload
    def recent(self,limit=30):
        with self.connect() as db:
            return [{"event_id":r[0],"data":json.loads(r[1]),"created_at":r[2]} for r in db.execute("SELECT event_id,data,created_at FROM events ORDER BY created_at DESC,rowid DESC LIMIT ?",(max(1,min(limit,100)),))]
