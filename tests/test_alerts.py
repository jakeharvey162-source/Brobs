import unittest
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
    def test_no_live_orders(self):
        self.assertFalse(hasattr(self.s,"live_broker"))
    def test_reject_market(self):
        with self.assertRaises(ValueError):self.s.handle({"secret":self.s.token,"event_id":"two","symbol":"BTCUSD","market":"invalid","action":"buy","price":100})

if __name__=="__main__":unittest.main()
