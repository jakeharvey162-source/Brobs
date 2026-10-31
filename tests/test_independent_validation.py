"""Regression checks for the offline, non-promoting shadow comparison."""
import copy
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from brobs.fx_research import replay
from brobs.independent_validation import (audit_bars, compare_shadow,
                                          screened_replay, screening_signal)
from brobs.loss_lab import available_news, entry_regime

UTC = timezone.utc


def bars(n=630):
    first = datetime(2025, 1, 1, tzinfo=UTC)
    result = []
    for i in range(n):
        price = 1.1 + .000025 * i + .00015 * (i % 23)
        result.append(dict(timestamp=first + timedelta(hours=i),
                           open=price, high=price + .0005,
                           low=price - .0005, close=price + .0001,
                           volume=100))
    return result


class IndependentValidationTests(unittest.TestCase):
    def test_audit_counts_gaps_without_inventing_candles(self):
        rows = bars(150)
        for row in rows[90:]:
            row["timestamp"] += timedelta(hours=3)
        report = audit_bars(rows)
        self.assertEqual(report["rows"], 150)
        self.assertEqual(report["gap_count"], 1)
        self.assertEqual(report["largest_gap_hours"], 4)
        self.assertTrue(report["gaps_not_filled"])

    def test_audit_rejects_duplicate_timestamps(self):
        rows = bars(120)
        rows[20]["timestamp"] = rows[19]["timestamp"]
        with self.assertRaises(ValueError):
            audit_bars(rows)

    def test_audit_rejects_bad_ohlc(self):
        rows = bars(120)
        rows[20]["high"] = rows[20]["low"] - 1
        with self.assertRaises(ValueError):
            audit_bars(rows)

    def test_audit_rejects_naive_timestamps(self):
        rows = bars(120)
        rows[20]["timestamp"] = rows[20]["timestamp"].replace(tzinfo=None)
        with self.assertRaises(ValueError):
            audit_bars(rows)

    def test_empty_screen_exactly_reproduces_baseline(self):
        rows = bars(180)
        baseline = replay(rows, 125)
        shadow, vetoed = screened_replay(rows, 125, frozenset())
        self.assertEqual(shadow, baseline)
        self.assertEqual(vetoed, 0)

    def test_future_rows_do_not_change_past_signal(self):
        rows = bars(150)
        regime = entry_regime(rows, rows[130]["timestamp"])
        first = screening_signal(rows[:130], 0, frozenset([regime]))
        later = copy.deepcopy(rows)
        for row in later[130:]:
            row["close"] *= 1.2
            row["high"] = max(row["high"], row["close"])
        second = screening_signal(later[:130], 0, frozenset([regime]))
        self.assertEqual(first, second)

    def test_screen_cannot_suppress_existing_position_exit(self):
        rows = bars(130)
        regime = entry_regime(rows, rows[-1]["timestamp"] + timedelta(microseconds=1))
        with patch("brobs.independent_validation.decide", return_value=("sell", [])):
            flat = screening_signal(rows, 0, frozenset([regime]))
            invested = screening_signal(rows, 1, frozenset([regime]))
        self.assertEqual(flat[0], "hold")
        self.assertEqual(invested[0], "sell")

    def test_news_at_same_instant_is_not_prior_knowledge(self):
        at = datetime(2025, 2, 1, tzinfo=UTC)
        def event(available):
            return dict(published_at=available, available_at=available,
                        event_label="archive", source_url="https://example.org/a")
        self.assertEqual(available_news([event(at), event(at - timedelta(seconds=1))], at),
                         [event(at - timedelta(seconds=1))])

    def test_report_is_immutable_paper_only_not_proven_improvement(self):
        output = compare_shadow(bars())
        self.assertFalse(output["execution_enabled"])
        self.assertFalse(output["auto_promotion"])
        self.assertFalse(output["improved_win_rate_verified"])
        self.assertTrue(output["evaluation"]["inspected_before"])
        self.assertEqual(output["evaluation"]["baseline"]["closed_trades"],
                         output["evaluation"]["baseline"]["wins"]
                         + output["evaluation"]["baseline"]["losses"]
                         + output["evaluation"]["baseline"]["breakeven"])
        screened = output["evaluation"]["screened"]
        self.assertAlmostEqual(screened["ending_equity"] - 10000,
                               screened["net_pnl"], places=3)
        self.assertIn("baseline_higher_cost", output["evaluation"])
        self.assertIn("screened_higher_cost", output["evaluation"])


if __name__ == "__main__":
    unittest.main()
