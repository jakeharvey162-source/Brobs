import csv
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from brobs.research_report import (
    DATASETS, Dataset, archive_comparisons, build_report, cash_metrics, dataset_report, main, markdown,
)


class ResearchReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self.spec = Dataset('fixture', 'crypto', 'BTC_USDT', 'fixture.csv', 3600)
        self.rows = []
        for i in range(180):
            at = datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i)
            close = 100 + i * .02 + math.sin(i / 8)
            self.rows.append(dict(timestamp=at.isoformat(), open=close-.05,
                                  high=close+.2, low=close-.2, close=close, volume=10))
        self.write_csv()

    def write_csv(self, rows=None):
        with (self.root/'fixture.csv').open('w', newline='') as target:
            writer = csv.DictWriter(target, fieldnames=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            writer.writeheader()
            writer.writerows(self.rows if rows is None else rows)

    def build(self, **kwargs):
        return build_report(self.root, self.root, [self.spec], **kwargs)

    def test_repeatable_json_and_markdown_without_wall_clock_or_network(self):
        with patch('socket.socket.connect', side_effect=AssertionError('network forbidden')):
            first = self.build(as_of='2024-02-01T00:00:00+00:00')
            second = self.build(as_of='2024-02-01T02:00:00+02:00')
        self.assertEqual(json.dumps(first, sort_keys=True, allow_nan=False),
                         json.dumps(second, sort_keys=True, allow_nan=False))
        self.assertEqual(markdown(first), markdown(second))
        self.assertNotIn(str(self.root), json.dumps(first))
        self.assertNotIn('generated_at', first)
        self.assertEqual(first['datasets'][0]['input_sha256'],
                         hashlib.sha256((self.root/'fixture.csv').read_bytes()).hexdigest())

    def test_insufficient_evidence_retains_cash_and_all_comparators(self):
        report = self.build()
        item = report['datasets'][0]
        self.assertEqual(report['status'], 'not_validated')
        self.assertIsNone(report['selected_parameters'])
        self.assertTrue(report['cash_fallback'])
        self.assertFalse(report['execution_enabled'])
        self.assertFalse(report['auto_promotion'])
        self.assertFalse(item['pristine_holdout'])
        self.assertEqual(item['contamination'], 'previously_inspected_not_unseen')
        self.assertIn('insufficient_closed_trade_sample', item['failure_reasons'])
        for key in ('baseline', 'sma', 'cash'):
            self.assertIn(key, item['later'])
            self.assertIn(key, item['later_cost_stress'])
        self.assertEqual(item['later']['cash'], cash_metrics())
        self.assertEqual(item['later']['cash']['return_pct'], 0)
        self.assertIsNone(item['later']['cash']['win_rate_pct'])
        self.assertEqual(len(item['training_folds']), 2)
        self.assertEqual(len(item['later_folds']), 3)

    def test_later_prices_cannot_change_training_folds(self):
        first = self.build()['datasets'][0]
        changed = [dict(row) for row in self.rows]
        for row in changed[int(len(changed)*.7):]:
            for field in ('open', 'high', 'low', 'close'):
                row[field] *= 10
        self.write_csv(changed)
        second = self.build()['datasets'][0]
        self.assertEqual(first['training_folds'], second['training_folds'])
        self.assertNotEqual(first['input_sha256'], second['input_sha256'])
        self.assertLess(first['training_folds'][-1]['last_bar'], first['later']['first_bar'])
        for fold in first['later_folds']:
            self.assertTrue(fold['capital_reset'])

    def test_invalid_or_incomplete_data_never_replayed(self):
        with patch('brobs.research_report.replay', side_effect=AssertionError('must not replay')):
            incomplete = self.build(as_of=self.rows[-1]['timestamp'])['datasets'][0]
            self.assertEqual(incomplete['data_status'], 'invalid')
            self.assertIn('Incomplete', incomplete['failure_reasons'][0])
            self.write_csv(self.rows[:50])
            short = self.build()['datasets'][0]
            self.assertEqual(short['data_status'], 'invalid')
            self.assertNotIn('later', short)

    def test_missing_data_has_no_invented_metrics(self):
        (self.root/'fixture.csv').unlink()
        with patch('brobs.research_report.replay', side_effect=AssertionError('must not replay')):
            item = self.build()['datasets'][0]
        self.assertEqual(item['data_status'], 'not_available')
        self.assertEqual(item['status'], 'not_validated')
        self.assertNotIn('later', item)
        self.assertNotIn('input_sha256', item)
        self.assertTrue(item['cash_fallback'])
        self.assertIn('no_replay_performed', item['failure_reasons'][0])

    def test_gap_is_reported_and_never_filled(self):
        self.write_csv(self.rows[:80] + self.rows[81:])
        item = self.build()['datasets'][0]
        self.assertEqual(item['dataset_rows'], 179)
        self.assertEqual(item['data_validation']['gap_audit']['missing_count'], 1)
        self.assertIn('missing_scheduled_candles_no_filling_performed', item['failure_reasons'])
        self.assertEqual(item['status'], 'not_validated')

    def test_supplied_closed_session_bars_are_not_claimed_calendar_valid(self):
        self.spec = replace(self.spec, market='forex', symbol='EUR_USD')
        item = self.build()['datasets'][0]
        self.assertGreater(item['data_validation']['gap_audit']['unexpected_closed_session_count'], 0)
        self.assertEqual(item['data_validation']['calendar_status'], 'issues_detected')
        self.assertIn('supplied_bars_during_expected_closed_sessions', item['failure_reasons'])
        self.assertEqual(item['status'], 'not_validated')

    def test_provenance_mismatch_blocks_replay(self):
        manifest = dict(normalized_csv_sha256='0'*64, sources=[])
        (self.root/'fixture.provenance.json').write_text(json.dumps(manifest))
        self.spec = replace(self.spec, provenance='fixture.provenance.json')
        with patch('brobs.research_report.replay', side_effect=AssertionError('must not replay')):
            item = self.build()['datasets'][0]
        self.assertEqual(item['data_status'], 'invalid')
        self.assertEqual(item['failure_reasons'], ['provenance_digest_mismatch'])

    def test_contradictory_provenance_identity_blocks_without_digest(self):
        for declarations, reason in [
            ({'symbol': 'ETHUSDT'}, 'provenance_symbol_mismatch'),
            ({'quote_currency': 'USD'}, 'provenance_quote_currency_mismatch'),
            ({'rows': 6552}, 'provenance_row_count_mismatch'),
            ({'rows': True}, 'invalid_provenance_row_count'),
        ]:
            with self.subTest(declarations=declarations):
                (self.root/'manifest.json').write_text(json.dumps(declarations))
                self.spec = replace(self.spec, provenance='manifest.json')
                with patch('brobs.research_report.replay', side_effect=AssertionError('must not replay')):
                    item = self.build()['datasets'][0]
                self.assertEqual(item['data_status'], 'invalid')
                self.assertIn(reason, item['failure_reasons'])

    def test_missing_digest_stays_unverified_and_manifest_path_is_portable(self):
        manifest = self.root/'manifest.json'
        manifest.write_text(json.dumps(dict(symbol='BTCUSDT', quote_currency='USDT', rows=180)))
        self.spec = replace(self.spec, provenance=str(manifest.resolve()))
        item = self.build()['datasets'][0]
        self.assertEqual(item['data_status'], 'available')
        self.assertEqual(item['provenance']['status'], 'not_independently_verified')
        self.assertIsNone(item['provenance']['normalized_csv_digest_match'])
        self.assertEqual(item['provenance']['manifest'], 'manifest.json')
        self.assertNotIn(str(self.root), json.dumps(item))

    def test_malformed_metadata_is_explicitly_invalid(self):
        (self.root/'manifest.json').write_text('{broken')
        self.spec = replace(self.spec, provenance='manifest.json')
        item = self.build()['datasets'][0]
        self.assertEqual(item['data_status'], 'invalid')
        self.assertEqual(item['provenance']['status'], 'invalid')
        self.spec = replace(self.spec, provenance=None, archives=('bad-report.json',))
        (self.root/'bad-report.json').write_text(json.dumps({'candidates': 'invalid'}))
        item = self.build()['datasets'][0]
        self.assertEqual(item['archived_experiments'][0]['status'], 'invalid')
        self.assertIn('invalid_archived_report_not_used_as_verified_evidence', item['failure_reasons'])

    def test_archived_comparisons_use_cash_for_every_phase_and_matching_baseline_only(self):
        payload = dict(
            baseline=dict(closed_trades=4, return_pct=2, net_pnl=200),
            candidates=[dict(parameters={'n': 1}, validation=dict(closed_trades=3, return_pct=8, net_pnl=800))],
            fixed_later_comparisons=[dict(parameters={'n': 1}, later_period=dict(closed_trades=5, return_pct=1, net_pnl=100))],
            selected_later_stress=dict(closed_trades=5, return_pct=-1, net_pnl=-100))
        comparisons = {x['metric_path']: x for x in archive_comparisons(payload)}
        training = comparisons['candidates.0.validation']
        self.assertEqual(training['phase'], 'training_validation')
        self.assertEqual(training['cash_comparison']['net_pnl_delta'], 800)
        self.assertEqual(training['baseline_comparison']['status'], 'not_available')
        later = comparisons['fixed_later_comparisons.0.later_period']
        self.assertEqual(later['cash_comparison']['return_pct_delta'], 1)
        self.assertEqual(later['baseline_comparison']['net_pnl_delta'], -100)
        self.assertEqual(later['baseline_comparison']['return_pct_delta'], -1)
        self.assertEqual(later['input_identity'], 'not_recorded_in_legacy_report')
        self.assertEqual(comparisons['selected_later_stress']['baseline_comparison']['status'], 'not_available')

    def test_every_archived_candidate_is_preserved_without_reranking(self):
        payload = dict(candidates=[dict(parameters={'n': i}, validation={'net_pnl': pnl})
                                   for i, pnl in enumerate([-4, 8, -2])],
                       selected_parameters=None, cash_fallback=True)
        path = self.root/'archive.json'
        path.write_text(json.dumps(payload))
        self.spec = replace(self.spec, archives=('archive.json',))
        item = self.build()['datasets'][0]
        archived = item['archived_experiments'][0]
        self.assertEqual(archived['status'], 'archived_not_recomputed')
        self.assertEqual(archived['candidate_count'], 3)
        self.assertEqual(archived['payload'], payload)
        self.assertEqual(archived['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertIsNone(item['selected_parameters'])
        self.assertTrue(item['cash_fallback'])
        self.assertIn('"n": 0', markdown(self.build()))
        self.assertIn('"n": 1', markdown(self.build()))
        self.assertIn('"n": 2', markdown(self.build()))

    def test_cost_stress_changes_cost_assumptions_not_strategy_parameters(self):
        item = self.build()['datasets'][0]
        base, stress = item['assumptions'], item['stress_assumptions']
        self.assertGreater(stress['spread_fraction'], base['spread_fraction'])
        self.assertGreater(stress['config']['slippage_fraction'], base['config']['slippage_fraction'])
        self.assertGreater(stress['config']['commission_fraction'], base['config']['commission_fraction'])
        for key in ('risk_fraction', 'stop_fraction', 'reward_risk', 'capital'):
            self.assertEqual(base['config'][key], stress['config'][key])

    def test_cli_writes_both_outputs_and_strict_missing_status(self):
        (self.root/'fixture.csv').unlink()
        json_path, markdown_path = self.root/'out.json', self.root/'out.md'
        result = main(['--csv', str(self.root/'fixture.csv'), '--market', 'crypto',
                       '--symbol', 'BTC_USDT', '--require-all-data',
                       '--output-json', str(json_path), '--output-markdown', str(markdown_path)])
        self.assertEqual(result, 1)
        self.assertEqual(json.loads(json_path.read_text())['status'], 'not_validated')
        self.assertIn('not_available', markdown_path.read_text())

    def test_existing_eurusd_baseline_counts_and_archive_are_preserved(self):
        result = dataset_report(DATASETS[0], 'research/data', 'research', '2026-10-29T00:00:00+00:00')
        baseline = result['later']['baseline']
        self.assertEqual((baseline['closed_trades'], baseline['wins'], baseline['losses']), (28, 11, 17))
        self.assertEqual(result['before_after_baseline']['status'], 'metrics_match')
        self.assertEqual(result['before_after_baseline']['differences'], {})
        self.assertEqual(result['data_validation']['gap_audit']['missing_count'], 0)


if __name__ == '__main__':
    unittest.main()
