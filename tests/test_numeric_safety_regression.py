"""Regression tests for numeric safety in the paper engine."""
import copy
import math
import unittest
from brobs.models import Instrument, Market, Portfolio
from brobs.paper import PaperBroker
from brobs.risk import RiskEngine, RiskConfig
from brobs.strategy import Signal, sma_signal

class NumericSafetyTests(unittest.TestCase):
    def test_nonfinite_history_holds(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                self.assertEqual(sma_signal([value,3,2,1,4],short=1,long=3),Signal.HOLD)

    def test_invalid_daily_anchor_halts(self):
        for value in (math.nan,math.inf,-math.inf,0,-1):
            p=Portfolio(equity_at_day_start=value)
            self.assertTrue(RiskEngine().check_halt(p,10000))

    def test_invalid_marked_equity_halts(self):
        for value in (math.nan,math.inf,-math.inf,0,-1):
            p=Portfolio()
            self.assertTrue(RiskEngine().check_halt(p,value))

    def test_bad_anchor_blocks_buy(self):
        p=Portfolio(equity_at_day_start=math.nan)
        b=PaperBroker(p,RiskEngine())
        self.assertIsNone(b.buy(Instrument('TEST',Market.CRYPTO),100,{'TEST':100}))
        self.assertEqual(p.positions,{})
        self.assertTrue(p.halted)

    def test_bad_marks_never_partially_sell(self):
        for prices in ({'A':80},{'A':80,'B':math.nan},{'A':80,'B':math.inf},{'A':80,'B':0},{'A':80,'B':-1}):
            with self.subTest(prices=prices):
                p=Portfolio()
                b=PaperBroker(p,RiskEngine(),fee_fraction=0,slippage_fraction=0)
                for symbol in ('A','B'):
                    self.assertIsNotNone(b.buy(Instrument(symbol,Market.CRYPTO),100,{'A':100,'B':100}))
                before=copy.deepcopy(p)
                fills=copy.deepcopy(b.fills)
                with self.assertRaises(ValueError):b.apply_stops(prices)
                self.assertEqual(p,before)
                self.assertEqual(b.fills,fills)

    def test_valid_crossovers(self):
        self.assertEqual(sma_signal([3,2,1,4],short=1,long=3),Signal.BUY)
        self.assertEqual(sma_signal([1,2,3,1],short=1,long=3),Signal.SELL)

    def test_nonfinite_config_rejected(self):
        for value in (math.nan,math.inf,-math.inf):
            with self.assertRaises(ValueError):RiskConfig(max_risk_fraction=value)

if __name__=='__main__':unittest.main()
