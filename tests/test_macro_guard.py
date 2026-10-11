"""Tests intentionally use file fixtures only; no broker orders or network."""
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import tempfile
import unittest
from brobs.macro_guard import gate

class TestMacroGuard(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"macro.json"
        self.now=datetime(2026, 10, 11, 17, tzinfo=timezone.utc)
        self.signal={"action":"buy","votes":{"trend":1}}
        self.report={"schema":"brobs-macro-v1","as_of":self.now.isoformat(),"reviewed":True,"holds":[{
          "symbols":["EUR_USD"],"starts_at":(self.now-timedelta(minutes=30)).isoformat(),
          "ends_at":(self.now+timedelta(minutes=30)).isoformat(),
          "source_urls":["https://example.org/economic-calendar"]
        }]}
    def save(self):
        self.path.write_text(json.dumps(self.report),encoding="utf-8")
    def test_blocks_new_entry_during_explicit_event(self):
        self.save()
        outcome=gate(self.signal,self.path,"EUR_USD",self.now)
        self.assertEqual(outcome["action"],"hold")
        self.assertEqual(outcome["macro_guard"]["reason"],"reviewed_high_impact_event")
    def test_does_not_impact_protective_or_flat_signals(self):
        self.save()
        for action in ("exit","hold"):
            obj={"action":action}
            self.assertEqual(gate(obj,self.path,"EUR_USD",self.now),obj)
    def test_other_symbol_not_paused(self):
        self.save()
        self.assertEqual(gate(self.signal,self.path,"GBP_USD",self.now)["action"],"buy")
    def test_missing_or_stale_report_fails_closed_when_enabled(self):
        self.assertEqual(gate(self.signal,self.path,"EUR_USD",self.now)["action"],"hold")
        self.report["as_of"]=(self.now-timedelta(hours=2)).isoformat()
        self.save()
        self.assertEqual(gate(self.signal,self.path,"EUR_USD",self.now)["action"],"hold")
    def test_requires_operator_review_and_evidence(self):
        self.report["reviewed"]=False
        self.save()
        self.assertEqual(gate(self.signal,self.path,"EUR_USD",self.now)["action"],"hold")
        self.report["reviewed"]=True
        self.report["holds"][0]["source_urls"]=[]
        self.save()
        self.assertEqual(gate(self.signal,self.path,"EUR_USD",self.now)["action"],"hold")
    def test_future_or_expired_hold_does_not_block(self):
        self.report["holds"][0]["starts_at"]=(self.now+timedelta(minutes=10)).isoformat()
        self.report["holds"][0]["ends_at"]=(self.now+timedelta(minutes=45)).isoformat()
        self.save()
        self.assertEqual(gate(self.signal,self.path,"EUR_USD",self.now)["action"],"buy")
if __name__=="__main__":unittest.main()
