import tempfile,unittest
from brobs.ledger import PaperLedger

class DashboardDataTests(unittest.TestCase):
    def test_dashboard_ledger_data(self):
        with tempfile.TemporaryDirectory() as d:
            ledger=PaperLedger(d+"/paper.db")
            self.assertEqual(ledger.load().cash,10000)
            self.assertEqual(ledger.recent(),[])

if __name__=="__main__":unittest.main()
