"""Regression checks: unsafe candle feeds must not open paper positions."""
import unittest
from datetime import datetime, timedelta, timezone
from brobs.fx_runner import tick


class InputGuardTests(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)

    def check_rejected(self, rows, expected):
        class Feed:
            def account_summary(self):
                return {"currency": "USD"}
            def candles(self, **kwargs):
                return rows
            def quotes(self, pairs):
                raise AssertionError("Quotes must not be requested for unsafe candles")
        class Book:
            def process(self, *args):
                raise AssertionError("Unsafe candles must never reach execution")
        with self.assertRaisesRegex(ValueError, expected):
            tick(Feed(), Book(), now=self.now)

    def valid_rows(self):
        return [
            {"timestamp": self.now - timedelta(hours=51-i), "close": 1.05 + i * .00001}
            for i in range(50)
        ]

    def test_empty_history(self):
        self.check_rejected([], "Insufficient")

    def test_short_history(self):
        self.check_rejected(self.valid_rows()[:29], "Insufficient")

    def test_duplicate_timestamp(self):
        rows = self.valid_rows()
        rows[-1]["timestamp"] = rows[-2]["timestamp"]
        self.check_rejected(rows, "Unsorted or duplicate")

    def test_out_of_order_timestamp(self):
        rows = self.valid_rows()
        rows[-1]["timestamp"] = rows[-3]["timestamp"]
        self.check_rejected(rows, "Unsorted or duplicate")

    def test_nonfinite_close(self):
        rows = self.valid_rows()
        rows[-1]["close"] = float("nan")
        self.check_rejected(rows, "Invalid candle close")

    def test_negative_close(self):
        rows = self.valid_rows()
        rows[-1]["close"] = -1
        self.check_rejected(rows, "Invalid candle close")

    def test_missing_close(self):
        rows = self.valid_rows()
        rows[-1].pop("close")
        self.check_rejected(rows, "Malformed candle")

if __name__ == "__main__":
    unittest.main()
