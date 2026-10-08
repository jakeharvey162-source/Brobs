import unittest
from brobs.agents import Coordinator,InformationAgent,VolatilityAgent
from brobs.models import Portfolio

class AgentTests(unittest.TestCase):
    def test_no_history_no_trade(self):
        action, votes = Coordinator().decide([100]*5, Portfolio(), 10000)
        self.assertEqual(action, "hold")
        self.assertEqual(len(votes), 5)
    def test_risk_veto(self):
        action, votes = Coordinator().decide([100]*30, Portfolio(), 9000)
        self.assertEqual(action, "hold")
        self.assertTrue(any(v.agent == "risk" and v.action == "veto" for v in votes))
    def test_unverified_news_abstains(self):
        self.assertEqual(InformationAgent().evaluate({"sentiment":"positive"}).action, "unknown")
    def test_extreme_volatility_veto(self):
        prices = [100 if i % 2 else 120 for i in range(30)]
        self.assertEqual(VolatilityAgent().evaluate(prices).action, "veto")
    def test_no_unilateral_buy(self):
        prices = [100]*25+[101,102,103,104,105,106]
        action,_ = Coordinator().decide(prices, Portfolio(),10000)
        self.assertIn(action, ("hold","buy"))

if __name__=="__main__": unittest.main()
