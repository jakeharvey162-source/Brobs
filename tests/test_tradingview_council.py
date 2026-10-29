"""Static safety and documentation checks for the read-only TradingView council.

These tests do not compile Pine; compilation still needs TradingView.
"""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PINE = ROOT / "tradingview" / "BROBS_COUNCIL.pine"
DOCS = ROOT / "docs" / "TRADINGVIEW_RESEARCH_COUNCIL.md"


class CouncilIndicatorContract(unittest.TestCase):
    def test_read_only_indicator_not_an_order_strategy(self):
        source = PINE.read_text(encoding="utf-8")
        self.assertTrue(source.startswith("//@version=6"))
        self.assertIn('indicator("BROBS Research Council', source)
        self.assertNotIn("strategy(", source)
        for forbidden in ("strategy.entry(", "strategy.exit(", "strategy.order(",
                          "strategy.close(", "alert(", "alertcondition("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_observation_and_uncertainty_labels(self):
        source = PINE.read_text(encoding="utf-8")
        for expected in ("Trend", "Momentum", "Volatility", "Data review",
                         "Mixed evidence: no conclusion",
                         "Wait for candle to close", "READ ONLY / NO ORDERS"):
            with self.subTest(expected=expected):
                self.assertIn(expected, source)

    def test_docs_do_not_claim_ai_or_profit(self):
        text = DOCS.read_text(encoding="utf-8")
        self.assertIn("not multiple LLM", text)
        self.assertIn("not a target to rewrite", text)
        self.assertIn("Pine compilation and chart rendering have not been validated", text)


if __name__ == "__main__":
    unittest.main()
