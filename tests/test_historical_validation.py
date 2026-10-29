"""Malformed history must fail before any simulated order can be evaluated."""
import csv
import tempfile
import unittest
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from brobs.fx_research import load_forex_csv, replay
from brobs.historical_validation import audit_gaps, validate_rows
from brobs.history import load_csv

UTC = timezone.utc


def bars(count=90, first=None):
    first = first or datetime(2025, 1, 6, tzinfo=UTC)
    return [dict(timestamp=first + timedelta(hours=i), open=1.1 + i * .0001,
                 high=1.102 + i * .0001, low=1.099 + i * .0001,
                 close=1.101 + i * .0001, volume=20) for i in range(count)]


class HistoricalValidationTests(unittest.TestCase):
    def test_duplicate_instant_with_different_timezone_is_rejected(self):
        rows = bars()
        rows[31]['timestamp'] = rows[30]['timestamp'].astimezone(timezone(timedelta(hours=2)))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            validate_rows(rows)

    def test_out_of_order_is_rejected_by_replay_before_signals(self):
        rows = bars()
        rows[40], rows[41] = rows[41], rows[40]
        calls = []
        with self.assertRaisesRegex(ValueError, 'out-of-order'):
            replay(rows, 30, signal_fn=lambda closes: calls.append(closes))
        self.assertEqual(calls, [])

    def test_timezone_offsets_normalize_without_mutating_input(self):
        rows = bars()
        offset = timezone(timedelta(hours=5, minutes=30))
        for row in rows:
            row['timestamp'] = row['timestamp'].astimezone(offset)
        before = deepcopy(rows)
        normalized = validate_rows(rows)
        self.assertEqual(rows, before)
        self.assertIs(normalized[0]['timestamp'].tzinfo, UTC)
        self.assertEqual(normalized[0]['timestamp'], before[0]['timestamp'])
        self.assertIsNot(normalized[0], rows[0])

    def test_naive_timestamps_need_explicit_legacy_opt_in(self):
        rows = bars()
        for row in rows:
            row['timestamp'] = row['timestamp'].replace(tzinfo=None)
        with self.assertRaisesRegex(ValueError, 'timezone'):
            validate_rows(rows)
        self.assertIs(validate_rows(rows, allow_naive_utc=True)[0]['timestamp'].tzinfo, UTC)

    def test_csv_loader_exposes_legacy_assumption_and_validates_headers(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bars.csv'
            with path.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                writer.writeheader()
                for row in bars():
                    writer.writerow({**row, 'timestamp': row['timestamp'].replace(tzinfo=None).isoformat()})
            with self.assertRaises(ValueError):
                load_csv(path)
            self.assertEqual(len(load_csv(path, allow_naive_utc=True)), 90)
            path.write_text('timestamp,close\n2025-01-01,1.1\n')
            with self.assertRaisesRegex(ValueError, 'columns'):
                load_csv(path)

    def test_invalid_prices_volume_and_missing_fields_rejected(self):
        corruptions = [
            ('open', True), ('low', float('nan')), ('high', float('inf')),
            ('close', 0), ('volume', -1), ('close', '1.1'), ('high', .5), ('low', 3),
        ]
        for field, value in corruptions:
            with self.subTest(field=field, value=value):
                rows = bars()
                rows[45][field] = value
                with self.assertRaises(ValueError):
                    replay(rows, 30)
        rows = bars()
        del rows[45]['volume']
        with self.assertRaises(ValueError):
            validate_rows(rows)

    def test_empty_and_insufficient_history_fail_explicitly(self):
        for rows in ([], bars(29)):
            with self.assertRaisesRegex(ValueError, 'observations'):
                validate_rows(rows)

    def test_ohlc_only_replay_remains_supported_without_fabricating_volume(self):
        rows = bars()
        for row in rows:
            del row['volume']
        captured = []
        def signal(history, side):
            captured.extend(history)
            return 'hold', []
        replay(rows, 60, row_signal_fn=signal)
        self.assertTrue(captured)
        self.assertTrue(all('volume' not in row for row in captured))
        for invalid in (True, float('nan'), -1):
            rows[50]['volume'] = invalid
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    replay(rows, 60, row_signal_fn=signal)

    def test_normalized_csv_missing_ohlcv_and_duplicate_headers_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.csv'
            path.write_text('datetime,close\n2025-01-01T00:00:00Z,1.1\n')
            with self.assertRaisesRegex(ValueError, 'OHLCV'):
                load_forex_csv(path)
            path.write_text('timestamp,open,high,low,close,volume,close\n')
            with self.assertRaisesRegex(ValueError, 'duplicate columns'):
                load_csv(path)

    def test_missing_crypto_and_forex_weekday_candles_rejected(self):
        rows = bars(50)
        del rows[35]
        for market in ('crypto', 'forex'):
            with self.subTest(market=market):
                audit = audit_gaps(rows, 3600, market)
                self.assertEqual(audit['missing_count'], 1)
                with self.assertRaisesRegex(ValueError, 'Missing 1'):
                    replay(rows, 30, interval=3600, market=market)

    def test_forex_weekend_calendar_handles_both_dst_offsets(self):
        for friday, sunday in [('2025-01-10T21:00:00Z', '2025-01-12T22:00:00Z'),
                               ('2025-07-11T20:00:00Z', '2025-07-13T21:00:00Z')]:
            rows = [dict(bars(1)[0], timestamp=friday), dict(bars(1)[0], timestamp=sunday)]
            audit = audit_gaps(rows, 3600, 'forex')
            self.assertEqual(audit['missing_count'], 0)
            self.assertEqual(audit['expected_closures'], 48)
            validate_rows(rows, min_rows=2, interval=3600, market='forex')

    def test_stock_weekend_and_recurring_holiday_not_missing_bars(self):
        rows = [dict(bars(1)[0], timestamp='2025-07-03T00:00:00Z'),
                dict(bars(1)[0], timestamp='2025-07-07T00:00:00Z')]
        audit = audit_gaps(rows, 86400, 'stock')
        self.assertEqual(audit['missing_count'], 0)
        self.assertEqual(audit['expected_closures'], 3)
        self.assertIn('exceptional', audit['calendar_limitation'])
        rows[1]['timestamp'] = '2025-07-08T00:00:00Z'
        with self.assertRaisesRegex(ValueError, 'Missing 1'):
            validate_rows(rows, min_rows=2, interval=86400, market='stock')

    def test_stock_session_dates_cross_dst_without_false_missing_bars(self):
        for friday, monday, elapsed_hours in [
            ('2024-03-08T09:30:00-05:00', '2024-03-11T09:30:00-04:00', 71),
            ('2024-11-01T09:30:00-04:00', '2024-11-04T09:30:00-05:00', 73),
        ]:
            with self.subTest(friday=friday):
                rows = [dict(bars(1)[0], timestamp=friday), dict(bars(1)[0], timestamp=monday)]
                normalized = validate_rows(rows, min_rows=2, interval=86400, market='stock')
                self.assertEqual((normalized[1]['timestamp'] - normalized[0]['timestamp']).total_seconds() / 3600, elapsed_hours)
                audit = audit_gaps(rows, 86400, 'stock')
                self.assertEqual(audit['missing_count'], 0)
                self.assertEqual(audit['expected_closures'], 2)
                # Equivalent instants can be represented using unrelated offsets.
                equivalent = [{**row, 'timestamp': stamp['timestamp'].astimezone(timezone(timedelta(hours=9)))}
                              for row, stamp in zip(rows, normalized)]
                self.assertEqual(audit_gaps(equivalent, 86400, 'stock'), audit)

    def test_stock_session_date_grid_detects_missing_weekday_across_dst(self):
        rows = [dict(bars(1)[0], timestamp='2024-03-08T09:30:00-05:00'),
                dict(bars(1)[0], timestamp='2024-03-12T09:30:00-04:00')]
        audit = audit_gaps(rows, 86400, 'stock')
        self.assertEqual(audit['missing_count'], 1)
        self.assertEqual(audit['missing_timestamps_sample'], ['2024-03-11T13:30:00+00:00'])
        with self.assertRaisesRegex(ValueError, 'Missing 1'):
            validate_rows(rows, min_rows=2, interval=86400, market='stock')

    def test_daily_stock_conventions_cannot_be_mixed_or_guessed(self):
        rows = [dict(bars(1)[0], timestamp='2024-03-08T00:00:00Z'),
                dict(bars(1)[0], timestamp='2024-03-11T09:30:00-04:00')]
        with self.assertRaisesRegex(ValueError, 'timestamp convention'):
            validate_rows(rows, min_rows=2, interval=86400, market='stock')

    def test_supplied_stock_holiday_and_forex_weekend_candles_rejected(self):
        cases = [
            ('stock', 86400, ['2025-07-03T00:00:00Z', '2025-07-04T00:00:00Z', '2025-07-07T00:00:00Z']),
            ('forex', 3600, ['2025-01-10T21:00:00Z', '2025-01-11T21:00:00Z', '2025-01-12T22:00:00Z']),
        ]
        for market, interval, stamps in cases:
            with self.subTest(market=market):
                rows = [dict(bars(1)[0], timestamp=stamp) for stamp in stamps]
                audit = audit_gaps(rows, interval, market)
                self.assertEqual(audit['missing_count'], 0)
                self.assertEqual(audit['unexpected_closed_session_count'], 1)
                self.assertEqual(audit['unexpected_closed_session_timestamps_sample'],
                                 [datetime.fromisoformat(stamps[1].replace('Z', '+00:00')).isoformat()])
                with self.assertRaisesRegex(ValueError, 'closed market sessions'):
                    validate_rows(rows, min_rows=3, interval=interval, market=market)

    def test_unexpected_closed_session_diagnostics_are_bounded(self):
        rows = bars(24 * 14)
        audit = audit_gaps(rows, 3600, 'forex')
        self.assertGreater(audit['unexpected_closed_session_count'], 20)
        self.assertEqual(len(audit['unexpected_closed_session_timestamps_sample']), 20)

    def test_calendar_expansion_bound_covers_all_gaps_not_only_each_gap(self):
        rows = [dict(bars(1)[0], timestamp=stamp) for stamp in [
            '2025-01-03T00:00:00Z', '2025-01-06T00:00:00Z',
            '2025-01-07T00:00:00Z', '2025-01-10T00:00:00Z',
        ]]
        # Each gap expands at most two dates, but the total exceeds three.
        with patch('brobs.historical_validation.MAX_GAP_STEPS', 3):
            with self.assertRaisesRegex(ValueError, 'bounded calendar audit limit'):
                audit_gaps(rows, 86400, 'stock')

    def test_stock_new_year_saturday_keeps_preceding_friday_open(self):
        rows = [dict(bars(1)[0], timestamp=stamp) for stamp in [
            '2021-12-31T00:00:00Z', '2022-01-03T00:00:00Z',
        ]]
        audit = audit_gaps(rows, 86400, 'stock')
        self.assertEqual(audit['missing_count'], 0)
        self.assertEqual(audit['unexpected_closed_session_count'], 0)
        self.assertEqual(audit['expected_closures'], 2)
        validate_rows(rows, min_rows=2, interval=86400, market='stock')
        rows[0]['timestamp'] = '2021-12-30T00:00:00Z'
        self.assertEqual(audit_gaps(rows, 86400, 'stock')['missing_timestamps_sample'],
                         ['2021-12-31T00:00:00+00:00'])

    def test_stock_new_year_sunday_observes_monday(self):
        rows = [dict(bars(1)[0], timestamp=stamp) for stamp in [
            '2022-12-30T00:00:00Z', '2023-01-03T00:00:00Z',
        ]]
        audit = audit_gaps(rows, 86400, 'stock')
        self.assertEqual(audit['missing_count'], 0)
        self.assertEqual(audit['expected_closures'], 3)
        rows.insert(1, dict(bars(1)[0], timestamp='2023-01-02T00:00:00Z'))
        with self.assertRaisesRegex(ValueError, 'closed market sessions'):
            validate_rows(rows, min_rows=3, interval=86400, market='stock')

    def test_stock_mlk_holiday_observation_begins_in_1998(self):
        for monday, expected_closed in [('1997-01-20T00:00:00Z', 0),
                                         ('1998-01-19T00:00:00Z', 1)]:
            with self.subTest(monday=monday):
                row = dict(bars(1)[0], timestamp=monday)
                self.assertEqual(audit_gaps([row], 86400, 'stock')['unexpected_closed_session_count'], expected_closed)

    def test_off_interval_gaps_and_unsupported_calendars_fail(self):
        rows = bars()
        rows[-1]['timestamp'] += timedelta(minutes=10)
        with self.assertRaisesRegex(ValueError, 'aligned'):
            validate_rows(rows, interval=3600)
        with self.assertRaisesRegex(ValueError, 'calendar'):
            validate_rows(bars(), interval=3600, market='stock')

    def test_as_of_excludes_incomplete_and_future_bar(self):
        rows = bars()
        last = rows[-1]['timestamp']
        for as_of in (last - timedelta(seconds=1), last + timedelta(minutes=59, seconds=59)):
            with self.subTest(as_of=as_of):
                with self.assertRaisesRegex(ValueError, 'Incomplete'):
                    replay(rows, 30, interval=3600, market='crypto', as_of=as_of)
        validate_rows(rows, interval=3600, as_of=last + timedelta(hours=1))
        with self.assertRaisesRegex(ValueError, 'explicit bar interval'):
            validate_rows(rows, as_of=last)

    def test_row_signal_prefix_never_contains_current_or_future_bar(self):
        rows = bars()
        captured = []
        def signal(history, side):
            captured.append([r['timestamp'] for r in history])
            return 'hold', []
        first = replay(rows, 60, row_signal_fn=signal)
        for index, history in enumerate(captured, 60):
            self.assertTrue(all(stamp < rows[index]['timestamp'] for stamp in history))
        expected_early = captured[:10]
        captured.clear()
        for row in rows[80:]:
            row.update(open=3.0, high=3.1, low=2.9, close=3.0)
        replay(rows, 60, row_signal_fn=signal)
        self.assertEqual(captured[:10], expected_early)
        self.assertEqual(first['closed_trades'], 0)

    def test_signal_and_replay_outputs_repeat_exactly_and_costs_not_erased(self):
        rows = bars(120)
        before = deepcopy(rows)
        normal = replay(rows, 70, include_trades=True)
        repeat = replay(rows, 70, include_trades=True)
        stressed = replay(rows, 70, spread=.0003, include_trades=True)
        self.assertEqual(normal, repeat)
        self.assertEqual(rows, before)
        self.assertGreater(normal['closed_trades'], 0)
        self.assertLessEqual(stressed['ending_equity'], normal['ending_equity'])

    def test_bundled_forex_and_stock_pass_declared_calendar_checks(self):
        for path, market, interval in [('research/data/EURUSD_1h.csv', 'forex', 3600),
                                       ('research/data/AAPL_1d.csv', 'stock', 86400)]:
            with self.subTest(path=path):
                rows = load_forex_csv(path, interval=interval, market=market)
                self.assertEqual(audit_gaps(rows, interval, market)['missing_count'], 0)


if __name__ == '__main__':
    unittest.main()
