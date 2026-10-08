import os,tempfile,unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
from brobs.ledger import PaperLedger
from brobs.forex_runner import run_once

class DurableRunnerTests(unittest.TestCase):
    def test_duplicate_concurrent_event_only_commits_once(self):
        with tempfile.TemporaryDirectory() as folder:
            db=PaperLedger(os.path.join(folder,'paper.db'))
            def write(_):
                def update(p):
                    p.cash-=100
                    return {'status':'recorded'}
                return db.process_once('same-event',update)
            with ThreadPoolExecutor(max_workers=6) as pool:
                results=list(pool.map(write,range(12)))
            self.assertEqual(sum(r is not None for r in results),1)
            self.assertEqual(db.load().cash,9900)
            self.assertEqual(len(db.recent()),1)
    def test_exception_rolls_back_portfolio_and_event(self):
        with tempfile.TemporaryDirectory() as folder:
            db=PaperLedger(os.path.join(folder,'paper.db'))
            def fail(p):
                p.cash=1
                raise RuntimeError('worker crash')
            with self.assertRaises(RuntimeError):db.process_once('crash',fail)
            self.assertEqual(db.load().cash,10000)
            self.assertFalse(db.has_event('crash'))
    def test_forex_runner_research_only(self):
        class Data:
            def candles(self,instrument):
                return [{'timestamp':datetime(2024,1,1,tzinfo=timezone.utc)+timedelta(hours=i),'close':1.1,'open':1.1} for i in range(40)]
        with tempfile.TemporaryDirectory() as folder:
            db=PaperLedger(os.path.join(folder,'paper.db'))
            r=run_once(Data(),db)
            self.assertEqual(r['status'],'research_only')
            self.assertEqual(r['fills'],[])
            self.assertEqual(db.load().cash,10000)
            self.assertEqual(run_once(Data(),db)['status'],'duplicate_candle')

if __name__=='__main__':unittest.main()
