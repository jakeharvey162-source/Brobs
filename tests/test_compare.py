import unittest
from datetime import datetime,timedelta,timezone
from brobs.compare import compare

class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.rows=[]
        for i in range(150):
            p=100+i*0.1
            self.rows.append({'timestamp':datetime(2023,1,1,tzinfo=timezone.utc)+timedelta(days=i),'open':p,'high':p+1,'low':p-1,'close':p,'volume':1000})
    def test_comparison(self):
        for market in ('crypto','forex','stock'):
            result=compare(self.rows,market=market)
            self.assertEqual(result['test_bars'],45)
            self.assertIn('multi_agent',result['results'])
            self.assertIn('buy_hold',result['results'])
            self.assertIsNone(result['profitability_ratio'])
    def test_short_data_rejected(self):
        with self.assertRaises(ValueError):compare(self.rows[:40])
    def test_capital_rejected(self):
        with self.assertRaises(ValueError):compare(self.rows,capital=0)

if __name__=='__main__':unittest.main()
