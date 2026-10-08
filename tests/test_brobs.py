import unittest
from brobs.models import Market, Instrument, Portfolio
from brobs.risk import RiskEngine, RiskConfig
from brobs.paper import PaperBroker
from brobs.strategy import sma_signal, Signal

class BrobsTests(unittest.TestCase):
    def test_markets(self):
        self.assertEqual(len(Market), 3)
    def test_no_signal_without_history(self):
        self.assertEqual(sma_signal([100] * 5), Signal.HOLD)
    def test_flat_history(self):
        self.assertEqual(sma_signal([100] * 30), Signal.HOLD)
    def test_position_sizing(self):
        self.assertLessEqual(RiskEngine().quantity(10000, 10000, 100) * 100, 1000.01)
    def test_daily_circuit_breaker(self):
        p = Portfolio()
        self.assertTrue(RiskEngine().check_halt(p, 9700))
        self.assertTrue(p.halted)
        self.assertTrue(RiskEngine().check_halt(p, 11000))
    def test_paper_fill_and_close(self):
        p = Portfolio()
        b = PaperBroker(p, RiskEngine())
        ins = Instrument("BTC-USD", Market.CRYPTO)
        self.assertIsNotNone(b.buy(ins, 100, {"BTC-USD":100}))
        self.assertIsNotNone(b.sell("BTC-USD", 105))
        self.assertEqual(len(b.fills), 2)
        self.assertFalse(p.positions)
    def test_no_leverage(self):
        p = Portfolio(cash=10, equity_at_day_start=10)
        b = PaperBroker(p, RiskEngine())
        b.buy(Instrument("TEST", Market.STOCK), 500, {"TEST":500})
        self.assertGreaterEqual(p.cash, -1e-8)
    def test_invalid_fees(self):
        with self.assertRaises(ValueError): PaperBroker(Portfolio(), RiskEngine(), -0.1)

if __name__ == "__main__": unittest.main()
