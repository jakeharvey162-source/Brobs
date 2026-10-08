import unittest,tempfile,os
from datetime import datetime,timedelta,timezone
from brobs.oanda_practice import PracticeData,BASE
from brobs.ledger import PaperLedger
from brobs.forex_runner import run_once
from brobs.models import Portfolio

class ForexTests(unittest.TestCase):
    def test_practice_only_and_complete_candles(self):
        def fake(path):
            self.assertIn("/v3/instruments/EUR_USD/candles?",path)
            return {"candles":[{"time":(datetime(2024,1,1,tzinfo=timezone.utc)+timedelta(hours=i)).isoformat(),"complete":True,"mid":{"o":"1.1","h":"1.2","l":"1.0","c":str(1.1+i/10000)}} for i in range(50)]+[{"complete":False}]}
        adapter=PracticeData("fake","practice-12345",fake)
        self.assertIn("fxpractice",BASE)
        self.assertEqual(len(adapter.candles()),50)
    def test_ledger_persists_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            db=PaperLedger(os.path.join(folder,"paper.db"))
            p=Portfolio();p.cash=9000
            self.assertTrue(db.save(p,"event1",{"action":"buy"}))
            self.assertFalse(db.save(p,"event1",{"action":"buy"}))
            self.assertEqual(PaperLedger(os.path.join(folder,"paper.db")).load().cash,9000)
            self.assertEqual(len(db.recent()),1)
    def test_runner_deduplicates_same_candle(self):
        class FakeData:
            def candles(self,instrument):
                return [{"timestamp":datetime(2024,1,1,tzinfo=timezone.utc)+timedelta(hours=i),"close":1.1,"open":1.1} for i in range(40)]
        with tempfile.TemporaryDirectory() as folder:
            db=PaperLedger(os.path.join(folder,"paper.db"))
            self.assertEqual(run_once(FakeData(),db)["status"],"research_only")
            self.assertEqual(run_once(FakeData(),db)["status"],"duplicate_candle")

if __name__=="__main__":unittest.main()
