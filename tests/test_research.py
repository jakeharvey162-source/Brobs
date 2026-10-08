import unittest,tempfile,csv,os
from datetime import datetime,timedelta,timezone
from brobs.history import load_csv
from brobs.backtest import backtest

class ResearchTests(unittest.TestCase):
    def test_historical_csv_and_backtest(self):
        fd,path=tempfile.mkstemp(suffix=".csv");os.close(fd)
        try:
            with open(path,"w",newline="") as f:
                w=csv.writer(f);w.writerow(["timestamp","open","high","low","close","volume"])
                for i in range(60):
                    p=100+(i%15);w.writerow([(datetime(2024,1,1,tzinfo=timezone.utc)+timedelta(days=i)).isoformat(),p,p+1,p-1,p,1000])
            rows=load_csv(path)
            for market in ("crypto","forex","stock"):
                result=backtest(rows,market=market)
                self.assertIn("max_drawdown_pct",result)
                self.assertGreater(result["final_equity"],0)
        finally: os.remove(path)
    def test_missing_data_rejected(self):
        with self.assertRaises(ValueError): backtest([])

if __name__=="__main__": unittest.main()
