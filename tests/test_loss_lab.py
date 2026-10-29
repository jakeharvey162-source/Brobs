"""Time-causal, paper-only loss diagnostics."""
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from brobs.loss_lab import (available_news, entry_regime, evaluate,
                            load_news_metadata, profile, timestamp)
from brobs.fx_research import load_forex_csv

UTC = timezone.utc
ROOT = Path(__file__).resolve().parents[1]


def bars(n=180):
    first = datetime(2025, 1, 1, tzinfo=UTC)
    result = []
    for i in range(n):
        value = 1.0 + .0001 * i + .0008 * ((i // 17) % 3)
        result.append(dict(timestamp=first + timedelta(hours=i),
                           open=value, high=value + .001, low=value - .001,
                           close=value, volume=1.0))
    return result


def sample_trade(when, pnl, reason="stop"):
    return dict(opened_at=when.isoformat(),
                closed_at=(when + timedelta(minutes=30)).isoformat(),
                pnl=pnl, reason=reason)


class LossResearchTests(unittest.TestCase):
    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            timestamp("2025-01-01T10:00:00")

    def test_future_and_delayed_news_do_not_leak(self):
        at = datetime(2025, 2, 1, 12, tzinfo=UTC)
        def event(published, available, label):
            return dict(published_at=published, available_at=available,
                        event_label=label, source_url="https://example.com/a")
        news = [
            event(at - timedelta(hours=3), at - timedelta(hours=2), "earlier"),
            event(at - timedelta(hours=2), at + timedelta(seconds=1), "not yet ingested"),
            event(at + timedelta(minutes=1), at + timedelta(minutes=1), "future publication"),
            event(at - timedelta(days=5), at - timedelta(days=5), "too old"),
        ]
        self.assertEqual([n["event_label"] for n in available_news(news, at)], ["earlier"])

    def test_csv_news_rejects_invalid_availability(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "news.csv"
            path.write_text("published_at,available_at,source_url,event_label\n"
                            "2025-01-02T00:00:00Z,2025-01-01T00:00:00Z,https://example.com/a,too soon\n")
            with self.assertRaises(ValueError):
                load_news_metadata(path)

    def test_csv_news_accepts_valid_metadata(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "news.csv"
            path.write_text("published_at,available_at,source_url,event_label\n"
                            "2025-01-01T00:00:00Z,2025-01-01T00:05:00Z,https://example.com/a,example\n")
            self.assertEqual(len(load_news_metadata(path)), 1)

    def test_future_bar_cannot_change_earlier_regime(self):
        rows = bars(150)
        at = rows[130]["timestamp"]
        old_regime = entry_regime(rows, at)
        future = bars(170)[150:]
        for bar in future:
            bar["close"] *= 1.1
            bar["high"] = max(bar["high"], bar["close"])
        self.assertEqual(entry_regime(rows + future, at), old_regime)

    def test_training_loss_flag_is_descriptive(self):
        rows = bars(180)
        at = rows[130]["timestamp"]
        losing = profile([sample_trade(at + timedelta(minutes=i), -1) for i in range(9)], rows)
        winning = profile([sample_trade(at + timedelta(minutes=i), 1) for i in range(9)], rows)
        self.assertTrue(losing["buckets"][0]["review_flag"])
        self.assertFalse(winning["buckets"][0]["review_flag"])

    def test_bad_pnl_rejected(self):
        rows = bars(180)
        with self.assertRaises(ValueError):
            profile([sample_trade(rows[130]["timestamp"], float("nan"))], rows)

    def test_historical_replay_unchanged_and_complete(self):
        path = ROOT / "research/data/EURUSD_1h.csv"
        if not path.exists():
            self.skipTest("Historical forex CSV not included")
        report = evaluate(load_forex_csv(path))
        stats = report["later"]["baseline"]
        self.assertEqual(stats["closed_trades"], 28)
        self.assertEqual(stats["wins"], 11)
        self.assertEqual(stats["losses"], 17)
        self.assertEqual(report["later"]["loss_profile"]["closed_trades"], stats["closed_trades"])
        self.assertFalse(report["execution_enabled"])
        self.assertEqual(report["news"]["metadata_rows"], 0)


if __name__ == "__main__":
    unittest.main()
