import unittest
import tempfile
from pathlib import Path
from brobs.alerts import PaperAlertService

class AlertTests(unittest.TestCase):
    def setUp(self):self.s=PaperAlertService("this-is-a-long-test-secret-12345")
    def test_paper_buy_and_idempotency(self):
        alert={"secret":self.s.token,"event_id":"one","symbol":"BTCUSD","market":"crypto","action":"buy","price":100}
        self.assertEqual(self.s.handle(alert)["status"],"paper_filled")
        self.assertEqual(self.s.handle(alert)["status"],"duplicate")
        self.assertEqual(len(self.s.broker.fills),1)
    def test_bad_secret(self):
        with self.assertRaises(PermissionError):self.s.handle({"secret":"wrong"})
    def test_forex_midpoint_alert_is_rejected(self):
        with self.assertRaises(ValueError):
            self.s.handle({'secret':self.s.token,'event_id':'fx','symbol':'EUR_USD','market':'forex','action':'buy','price':1.1})
    def test_operator_pause_blocks_new_entries_but_allows_exits(self):
        with tempfile.TemporaryDirectory() as folder:
            pause=Path(folder)/'pause.marker'
            service=PaperAlertService(self.s.token,pause_file=str(pause))
            def alert(key,action):
                return {"secret":service.token,"event_id":key,"symbol":"BTCUSD","market":"crypto","action":action,"price":100}
            self.assertEqual(service.handle(alert('buy1','buy'))['status'],'paper_filled')
            pause.touch()
            self.assertEqual(service.handle(alert('buy2','buy'))['status'],'paper_entries_paused')
            self.assertEqual(service.handle(alert('sell1','sell'))['status'],'paper_filled')
            self.assertEqual(service.broker.portfolio.positions,{})
            pause.unlink()
            self.assertEqual(service.handle(alert('buy2','buy'))['status'],'duplicate')
            self.assertEqual(service.handle(alert('buy3','buy'))['status'],'paper_filled')
    def test_no_live_orders(self):
        self.assertFalse(hasattr(self.s,"live_broker"))
    def test_reject_market(self):
        with self.assertRaises(ValueError):self.s.handle({"secret":self.s.token,"event_id":"two","symbol":"BTCUSD","market":"invalid","action":"buy","price":100})

if __name__=="__main__":unittest.main()
