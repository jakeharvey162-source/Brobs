"""Causal and complexity regressions for descriptive loss diagnostics."""
from datetime import datetime, timedelta, timezone
import unittest
from pathlib import Path

from brobs.loss_lab import available_news, entry_regime, evaluate, profile
from brobs.fx_research import load_forex_csv


UTC = timezone.utc


def bars(count=180):
    first = datetime(2025, 1, 1, tzinfo=UTC)
    return [dict(timestamp=first + timedelta(hours=i),
                 open=1 + .0001 * i, close=1 + .0001 * i,
                 high=1.001 + .0001 * i, low=.999 + .0001 * i,
                 volume=1.0) for i in range(count)]


def trade(at, pnl=-1, reason="stop"):
    return dict(opened_at=at.isoformat(),
                closed_at=(at + timedelta(minutes=30)).isoformat(),
                pnl=pnl, reason=reason)


def news(published, available=None, label="event"):
    return dict(published_at=published, available_at=available or published,
                source_url="https://example.com/archive", event_label=label)


class CountedList(list):
    """Count full input traversals without relying on wall-clock timings."""
    def __init__(self, values):
        super().__init__(values)
        self.traversals = 0

    def __iter__(self):
        self.traversals += 1
        return super().__iter__()


class ClosedCandleRegressions(unittest.TestCase):
    def test_mid_candle_entry_cannot_see_that_candles_close(self):
        rows = bars()
        at = rows[130]["timestamp"] + timedelta(minutes=30)
        expected = entry_regime(rows, at)
        rows[130] = {**rows[130], "close": 1000, "high": 1000}
        self.assertEqual(entry_regime(rows, at), expected)
        self.assertNotEqual(entry_regime(rows, at + timedelta(minutes=30)), expected)

    def test_explicit_bar_duration_controls_completion(self):
        rows = bars()
        at = rows[130]["timestamp"] + timedelta(minutes=30)
        rows[130] = {**rows[130], "close": 1000, "high": 1000}
        self.assertNotEqual(entry_regime(rows, at),
                            entry_regime(rows, at, bar_duration=timedelta(minutes=30)))
        for duration in (timedelta(0), timedelta(hours=-1), 3600, True):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                entry_regime(rows, at, bar_duration=duration)

    def test_equivalent_timezones_do_not_change_attribution(self):
        rows = bars()
        at = rows[130]["timestamp"]
        self.assertEqual(entry_regime(rows, at),
                         entry_regime(rows, at.astimezone(timezone(timedelta(hours=2)))))

    def test_direct_profile_rejects_unordered_or_duplicate_candles(self):
        rows = bars()
        for replacement in (rows[99], rows[101]):
            malformed = rows.copy()
            malformed[100] = replacement
            with self.subTest(replacement=replacement), self.assertRaises(ValueError):
                profile([trade(rows[130]["timestamp"])], malformed)

    def test_candle_and_news_inputs_are_indexed_once_per_profile(self):
        rows = CountedList(bars())
        at = rows[130]["timestamp"]
        events = CountedList([news(at - timedelta(hours=2))])
        trades = [trade(at + timedelta(seconds=i)) for i in range(40)]
        result = profile(trades, rows, events)
        self.assertEqual(result["entries_with_prior_news_metadata"], len(trades))
        # Per-trade rescanning would traverse both inputs 40 times.
        self.assertLessEqual(rows.traversals, 2)
        self.assertEqual(events.traversals, 1)


class ArchivedNewsRegressions(unittest.TestCase):
    def setUp(self):
        self.at = datetime(2025, 2, 1, 12, tzinfo=UTC)

    def test_delayed_ingestion_cannot_refresh_an_old_publication(self):
        old = news(self.at - timedelta(days=5), self.at - timedelta(minutes=1))
        self.assertEqual(available_news([old], self.at), [])
        rows = bars()
        at = rows[130]["timestamp"]
        old = news(at - timedelta(days=5), at - timedelta(minutes=1))
        self.assertEqual(profile([trade(at)], rows, [old])["entries_with_prior_news_metadata"], 0)

    def test_future_availability_and_future_publication_never_qualify(self):
        events = [news(self.at - timedelta(hours=1), self.at + timedelta(seconds=1)),
                  news(self.at + timedelta(seconds=1))]
        self.assertEqual(available_news(events, self.at), [])

    def test_direct_metadata_validation_is_not_bypassed(self):
        invalid = [news(self.at, self.at - timedelta(seconds=1)),
                   {**news(self.at), "source_url": "http://example.com/article"},
                   {**news(self.at), "source_url": "https://user:password@example.com/article"},
                   {**news(self.at), "event_label": ""},
                   {**news(self.at), "available_at": self.at.replace(tzinfo=None)}]
        for event in invalid:
            with self.subTest(event=event), self.assertRaises(ValueError):
                available_news([event], self.at)

    def test_iso_offsets_normalize_and_order_is_deterministic(self):
        first = news((self.at - timedelta(hours=1)).isoformat(),
                     (self.at - timedelta(minutes=30)).astimezone(
                         timezone(timedelta(hours=2))).isoformat(), "first")
        second = news(self.at - timedelta(minutes=20), label="second")
        forward = available_news([first, second], self.at)
        reverse = available_news([second, first], self.at)
        self.assertEqual(forward, reverse)
        self.assertEqual([item["event_label"] for item in forward], ["first", "second"])
        self.assertTrue(all(item["available_at"].tzinfo == UTC for item in forward))

    def test_expiry_boundary_and_indexed_existence_agree(self):
        rows = bars()
        at = rows[130]["timestamp"]
        events = [news(at - timedelta(hours=24), at - timedelta(minutes=1), "boundary"),
                  news(at - timedelta(hours=25), at - timedelta(seconds=1), "old delayed"),
                  news(at + timedelta(hours=2), label="future")]
        query_times = [at - timedelta(seconds=2), at, at + timedelta(seconds=1),
                       at + timedelta(hours=2), at + timedelta(hours=27)]
        expected = sum(bool(available_news(events, point)) for point in query_times)
        result = profile([trade(point) for point in query_times], rows, events)
        self.assertEqual(result["entries_with_prior_news_metadata"], expected)
        self.assertEqual([item["event_label"] for item in available_news(events, at)], ["boundary"])

    def test_invalid_age_windows_fail_closed(self):
        for age in (0, -1, float("inf"), float("nan"), True, "24"):
            with self.subTest(age=age), self.assertRaises(ValueError):
                available_news([], self.at, max_age_hours=age)


class LossReasonRegressions(unittest.TestCase):
    def test_loss_reasons_exclude_profitable_and_breakeven_exits(self):
        rows = bars()
        at = rows[130]["timestamp"]
        trades = [trade(at, -2, "stop"), trade(at, 3, "target"),
                  trade(at, 0, "liquidate")]
        result = profile(iter(trades), rows)
        self.assertEqual(result["loss_reasons"], {"stop": 1})
        self.assertEqual(result["exit_reasons"], {"liquidate": 1, "stop": 1, "target": 1})
        self.assertEqual(result["closed_trades"], 3)
        self.assertEqual(result["buckets"][0]["breakeven"], 1)
        self.assertEqual(result["buckets"][0]["net_pnl"], 1)

    def test_direct_trade_records_fail_closed(self):
        rows = bars()
        at = rows[130]["timestamp"]
        invalid = [None, {}, {**trade(at), "pnl": True},
                   {**trade(at), "closed_at": (at - timedelta(seconds=1)).isoformat()},
                   {**trade(at), "reason": 1}]
        for record in invalid:
            with self.subTest(record=record), self.assertRaises(ValueError):
                profile([record], rows)

    def test_inspected_history_is_not_validation_or_promotion(self):
        dataset = Path(__file__).resolve().parents[1] / "research/data/EURUSD_1h.csv"
        report = evaluate(load_forex_csv(dataset))
        self.assertEqual(report["validation_status"], "not_validated")
        self.assertEqual(report["holdout_status"], "previously_inspected_contaminated")
        self.assertIsNone(report["selected_parameters"])
        self.assertTrue(report["cash_fallback"])
        self.assertFalse(report["execution_enabled"])
        self.assertEqual(report["later"]["baseline"]["closed_trades"], 28)


if __name__ == "__main__":
    unittest.main()
