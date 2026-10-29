"""Deterministic local historical reports; paper-only, with no strategy promotion.

This module reads CSV/JSON files and invokes the existing in-memory simulator.
It never fetches data, imports a broker gateway, or treats reused periods as an
unseen test. Archived experiments remain explicitly distinct from fresh replays.
"""
import argparse
from collections import Counter
from dataclasses import asdict, dataclass, replace
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import re

from .fx_research import load_forex_csv, replay
from .historical_validation import audit_gaps, timestamp
from .market_book import BOOKS, default_config
from .market_signals import signal


@dataclass(frozen=True)
class Dataset:
    name: str
    market: str
    symbol: str
    filename: str
    interval_seconds: int
    provenance: str | None = None
    archives: tuple = ()
    baseline_archive: str | None = None


DATASETS = (
    Dataset('eurusd-hourly', 'forex', 'EUR_USD', 'EURUSD_1h.csv', 3600,
            archives=('eurusd-holdout.json', 'forex-strategy-evaluation.json',
                      'reversion-evaluation.json', 'lab-forex-evaluation.json',
                      'winrate-forex-evaluation.json', 'grok-forex-evaluation.json',
                      'backtrader-current-reference.json', 'ml-evaluation.json'),
            baseline_archive='eurusd-holdout.json'),
    Dataset('aapl-daily', 'stock', 'AAPL', 'AAPL_1d.csv', 86400,
            archives=('stock-strategy-evaluation.json',),
            baseline_archive='stock-strategy-evaluation.json'),
    Dataset('btc-hourly', 'crypto', 'BTC_USDT', 'BTCUSDT_1h.csv', 3600,
            'BTCUSDT_1h.provenance.json',
            ('crypto-strategy-evaluation.json', 'grok-btc-evaluation.json'),
            'crypto-strategy-evaluation.json'),
    Dataset('btc-extended-hourly', 'crypto', 'BTC_USDT', 'BTCUSDT_2025_2026.csv', 3600,
            'BTCUSDT_2025_2026.provenance.json',
            ('lab-btc-evaluation.json', 'winrate-btc-evaluation.json')),
    Dataset('eth-hourly', 'crypto', 'ETH_USDT', 'ETHUSDT_1h.csv', 3600,
            'ETHUSDT_1h.provenance.json',
            ('lab-eth-evaluation.json', 'winrate-eth-evaluation.json',
             'grok-eth-evaluation.json')),
)
METRIC_KEYS = ('closed_trades', 'wins', 'losses', 'breakeven', 'net_pnl',
               'return_pct', 'profit_factor', 'max_drawdown_pct', 'win_rate_pct',
               'sample_win_rate_95pct_interval')
CONTAMINATION = 'previously_inspected_not_unseen'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_metadata(path):
    def reject_constant(value):
        raise ValueError('Non-finite JSON value: ' + value)
    payload = json.loads(Path(path).read_text(encoding='utf-8'), parse_constant=reject_constant)
    if not isinstance(payload, dict):
        raise ValueError('Metadata must be a JSON object')
    return payload


def cash_metrics(capital=10000):
    return dict(closed_trades=0, wins=0, losses=0, breakeven=0, net_pnl=0,
                return_pct=0, ending_equity=capital, profit_factor=None,
                max_drawdown_pct=0, win_rate_pct=None,
                sample_win_rate_95pct_interval=None, evidence='no_trades',
                halted_reason=None, loss_reasons={})


def assumptions(market, stress=False):
    cfg = default_config(market)
    if stress:
        # Match the existing FX reference and multi-market cost-stress models.
        cfg = replace(cfg, commission_fraction=cfg.commission_fraction + .00005,
                      slippage_fraction=cfg.slippage_fraction * (1 if market == 'forex' else 2))
    return dict(config=asdict(cfg),
                spread_absolute=(.0003 if stress else .00015) if market == 'forex' else None,
                spread_fraction=(.001 if stress else .0005) if market != 'forex' else None,
                account_currency='USDT' if market == 'crypto' else 'USD',
                leverage=1, signal_fill='previous_closed_bars_to_next_open',
                intrabar='stop_first_if_stop_and_target_both_touch',
                final_position='liquidated_at_last_close',
                unmodeled=['swaps', 'funding', 'dividends', 'corporate_actions',
                           'order_book_depth', 'partial_fills', 'live_latency'])


def run(rows, start, market, symbol, strategy='baseline', stress=False):
    costs = assumptions(market, stress)
    cfg = replace(default_config(market), **costs['config'])
    kwargs = dict(config=cfg, book_class=BOOKS[market], symbol=symbol, include_trades=True)
    if market == 'forex':
        kwargs['spread'] = costs['spread_absolute']
    else:
        kwargs['spread_fraction'] = costs['spread_fraction']
    if strategy == 'sma':
        kwargs['mode'] = 'sma'
    elif market != 'forex':
        kwargs['row_signal_fn'] = lambda history, side: signal(history, 'trend', side, 10, False)
    result = replay(rows, start, **kwargs)
    trades = result.pop('trades')
    result['loss_reasons'] = dict(sorted(Counter(
        t.get('reason', 'unknown') for t in trades if t['pnl'] < -1e-9).items()))
    return result


def segment(rows, start, end, market, symbol):
    """Independent fold capital/reset; preceding bars are warm-up only."""
    return dict(first_bar=rows[start]['timestamp'].isoformat(),
                last_bar=rows[end - 1]['timestamp'].isoformat(), bars=end-start,
                first_evaluation_index=start, end_exclusive_index=end,
                capital_reset=True, prior_bars='indicator_warmup_only',
                baseline=run(rows[:end], start, market, symbol),
                sma=run(rows[:end], start, market, symbol, 'sma'),
                cash=cash_metrics(default_config(market).capital))


def archive_comparisons(payload):
    """Compare each recorded phase to cash and only a matching archived phase.

    Training scores must never be compared to a later-period baseline. Matching
    within an old report is still descriptive: it does not verify that report's
    input identity or execution model independently.
    """
    results = []

    def walk(item, path=(), parameters=None):
        if isinstance(item, list):
            for i, child in enumerate(item):
                walk(child, path + (i,), parameters)
        elif isinstance(item, dict):
            parameters = item.get('parameters', parameters)
            if 'closed_trades' in item and 'return_pct' in item:
                training = bool(path and (path[0] == 'candidates' or
                                any(part in ('validation', 'validation_folds') for part in path)))
                label = 'training_validation' if training else 'archived_reused_period'
                baseline = baseline_path = None
                if not training:
                    first = path[0] if path else None
                    if first in ('baseline', 'later_period', 'selected_later', 'fixed_later', 'fixed_later_comparisons'):
                        baseline, baseline_path = payload.get('baseline'), 'baseline'
                    elif first in ('baseline_cost_stress', 'cost_stress', 'fixed_cost_stress',
                                   'selected_cost_stress', 'selected_later_stress'):
                        baseline, baseline_path = payload.get('baseline_cost_stress'), 'baseline_cost_stress'
                    elif first == 'results':
                        baseline, baseline_path = payload.get('results', {}).get('multi_agent'), 'results.multi_agent'
                comparable = (isinstance(baseline, dict) and 'net_pnl' in baseline
                              and 'net_pnl' in item and 'return_pct' in baseline)
                baseline_comparison = dict(status='not_available',
                    reason='No baseline recorded for this same archived phase and cost scenario')
                if comparable:
                    baseline_comparison = dict(status='descriptive_same_archive_phase',
                        baseline_metric_path=baseline_path,
                        net_pnl_delta=round(item['net_pnl']-baseline['net_pnl'], 8),
                        return_pct_delta=round(item['return_pct']-baseline['return_pct'], 8),
                        input_and_cost_verification='not_independently_verified')
                metric_path = '.'.join(str(part) for part in path) or '<root>'
                comparison = dict(metric_path=metric_path, phase=label,
                    cash_comparison=dict(status='descriptive_zero_return_cash',
                                         net_pnl_delta=item.get('net_pnl'),
                                         return_pct_delta=item['return_pct']),
                    baseline_comparison=baseline_comparison,
                    input_sha256=payload.get('input_sha256'),
                    input_identity='recorded_not_independently_certified' if payload.get('input_sha256') else 'not_recorded_in_legacy_report',
                    contamination=CONTAMINATION)
                if parameters is not None:
                    comparison['parameters'] = parameters
                results.append(comparison)
                return
            for key, child in item.items():
                walk(child, path + (key,), parameters)
    walk(payload)
    return results


def archived_reports(spec, research_dir):
    """Keep every declared candidate, including failures; never rank or promote."""
    reports = []
    for filename in spec.archives:
        path = Path(research_dir) / filename
        if not path.is_file():
            reports.append(dict(file=filename, status='not_available'))
            continue
        try:
            payload = read_metadata(path)
            candidates = payload.get('candidates', [])
            if not isinstance(candidates, list) or any(not isinstance(c, dict) for c in candidates):
                raise ValueError('Archived candidates must be an array of objects')
            comparisons = archive_comparisons(payload)
        except (ValueError, TypeError, UnicodeError) as exc:
            reports.append(dict(file=filename, sha256=sha256(path), status='invalid',
                                failure_reason='Invalid archived report: ' + str(exc)))
            continue
        reports.append(dict(file=filename, sha256=sha256(path),
                            status='archived_not_recomputed',
                            candidate_count=len(candidates),
                            contamination=CONTAMINATION,
                            input_sha256=payload.get('input_sha256'),
                            phase_comparisons=comparisons,
                            payload=payload))
    return reports


def provenance(spec, data_dir, csv_path):
    result = dict(status='not_independently_verified', manifest=None,
                  normalized_csv_digest_match=None,
                  caveat='File integrity and recorded attribution do not certify vendor quality or a trading edge')
    manifest_path = Path(data_dir) / spec.provenance if spec.provenance else None
    if manifest_path and manifest_path.is_file():
        try:
            payload = read_metadata(manifest_path)
        except (ValueError, UnicodeError) as exc:
            result.update(status='invalid', errors=['Invalid provenance metadata: ' + str(exc)],
                          manifest=manifest_path.name, manifest_sha256=sha256(manifest_path))
            return result
        result.update(manifest=manifest_path.name, manifest_sha256=sha256(manifest_path),
                      metadata=payload)
        errors = []
        if 'symbol' in payload:
            declared_symbol = payload['symbol']
            if not isinstance(declared_symbol, str) or declared_symbol.replace('_', '') != spec.symbol.replace('_', ''):
                errors.append('provenance_symbol_mismatch')
        expected_currency = 'USDT' if spec.market == 'crypto' else 'USD'
        if 'quote_currency' in payload and payload['quote_currency'] != expected_currency:
            errors.append('provenance_quote_currency_mismatch')
        if 'rows' in payload and (type(payload['rows']) is not int or payload['rows'] < 1):
            errors.append('invalid_provenance_row_count')
        expected = payload.get('normalized_csv_sha256')
        if expected is not None and (not isinstance(expected, str) or not re.fullmatch('[0-9a-fA-F]{64}', expected)):
            errors.append('invalid_normalized_csv_digest')
        elif csv_path.is_file() and expected:
            result['normalized_csv_digest_match'] = sha256(csv_path) == expected.lower()
        if errors:
            result.update(status='invalid', errors=errors)
    elif spec.provenance:
        result.update(status='invalid', errors=['provenance_manifest_not_available'],
                      manifest=Path(spec.provenance).name)
    else:
        notice = Path(data_dir) / 'PROVENANCE.md'
        if notice.is_file():
            result.update(attribution_file='PROVENANCE.md', attribution_sha256=sha256(notice))
    return result


def compare_archive(spec, archives, current):
    original = next((a for a in archives if a['file'] == spec.baseline_archive), None)
    if original is None or original.get('status') != 'archived_not_recomputed':
        return dict(status='not_available', reason='No matching archived baseline report')
    payload = original['payload']
    before = (payload.get('results', {}).get('multi_agent') if spec.market == 'forex'
              else payload.get('baseline'))
    if before is None:
        return dict(status='not_available', reason='Archive has no comparable baseline')
    before = {key: before.get(key) for key in METRIC_KEYS}
    after = {key: current.get(key) for key in METRIC_KEYS}
    differences = {key: dict(before=before[key], after=after[key])
                   for key in METRIC_KEYS if before[key] != after[key]}
    return dict(status='metrics_match' if not differences else 'metrics_differ',
                archive_file=original['file'], archive_sha256=original['sha256'],
                archive_input_sha256=original.get('input_sha256'),
                input_identity='not_recorded_in_legacy_report' if not original.get('input_sha256') else 'recorded',
                before=before, after=after, differences=differences,
                caveat='A metric match is not independent data verification; costs and input digests must also be reviewed')


def dataset_report(spec, data_dir, research_dir, as_of=None):
    if spec.market not in BOOKS or spec.symbol not in BOOKS[spec.market].allowed_symbols:
        raise ValueError('Unsupported market or paper symbol')
    path = Path(data_dir) / spec.filename
    archives = archived_reports(spec, research_dir)
    result = dict(name=spec.name, market=spec.market, symbol=spec.symbol,
                  file=spec.filename, status='not_validated', data_status='not_available',
                  interval_seconds=spec.interval_seconds, contamination=CONTAMINATION,
                  pristine_holdout=False, execution_enabled=False,
                  selected_parameters=None, cash_fallback=True, auto_promotion=False,
                  provenance=provenance(spec, data_dir, path),
                  archived_experiments=archives, failure_reasons=[])
    if not path.is_file():
        result['failure_reasons'] = ['source_csv_not_available_no_replay_performed']
        return result
    result['input_sha256'] = sha256(path)
    if result['provenance']['status'] == 'invalid':
        result.update(data_status='invalid', failure_reasons=result['provenance']['errors'])
        return result
    if result['provenance']['normalized_csv_digest_match'] is False:
        result.update(data_status='invalid', failure_reasons=['provenance_digest_mismatch'])
        return result
    try:
        rows = load_forex_csv(path)
        metadata_rows = result['provenance'].get('metadata', {}).get('rows')
        if metadata_rows is not None and metadata_rows != len(rows):
            result.update(data_status='invalid', failure_reasons=['provenance_row_count_mismatch'])
            return result
        if len(rows) < 100:
            raise ValueError('At least 100 bars required for chronological report partitions')
        if as_of is not None and rows[-1]['timestamp'] + timedelta(seconds=spec.interval_seconds) > timestamp(as_of):
            raise ValueError('Incomplete current or future historical bar')
        gap_audit = audit_gaps(rows, spec.interval_seconds, spec.market)
    except (ValueError, KeyError, TypeError) as exc:
        result.update(data_status='invalid', failure_reasons=['invalid_historical_data: ' + str(exc)])
        return result
    result.update(data_status='available', dataset_rows=len(rows),
                  first_bar=rows[0]['timestamp'].isoformat(),
                  last_bar=rows[-1]['timestamp'].isoformat(),
                  data_validation=dict(structure='passed', gap_audit=gap_audit,
                                       completeness='passed' if as_of is not None else 'not_checked_no_as_of',
                                       calendar_status='issues_detected' if (gap_audit['missing_count'] or gap_audit.get('unexpected_closed_session_count', 0)) else 'no_issues_detected_by_limited_calendar',
                                       gap_handling='No filling/interpolation; descriptive replay retains supplied observations'),
                  assumptions=assumptions(spec.market), stress_assumptions=assumptions(spec.market, True))
    n = len(rows)
    cut = int(n * .7)
    early = max(30, int(n * .3))
    middle = max(early + 1, int(n * .5))
    result['partitions'] = dict(warmup_bars=early, selection_end_index=cut,
                                later_start_index=cut, later_bars=n-cut,
                                rule='Fixed 30/50/70 percent boundaries, no selection by reported results')
    result['training_folds'] = [segment(rows, early, middle, spec.market, spec.symbol),
                                segment(rows, middle, cut, spec.market, spec.symbol)]
    result['later'] = segment(rows, cut, n, spec.market, spec.symbol)
    edges = [cut + (n-cut)*i//3 for i in range(4)]
    result['later_folds'] = [segment(rows, edges[i], edges[i+1], spec.market, spec.symbol) for i in range(3)]
    result['later_cost_stress'] = dict(baseline=run(rows, cut, spec.market, spec.symbol, stress=True),
                                       sma=run(rows, cut, spec.market, spec.symbol, 'sma', True),
                                       cash=cash_metrics(default_config(spec.market).capital))
    baseline = result['later']['baseline']
    result['before_after_baseline'] = compare_archive(spec, archives, baseline)
    result['comparison_to_cash'] = dict(net_pnl_delta=baseline['net_pnl'],
                                        return_pct_delta=baseline['return_pct'],
                                        independently_validated_advantage=False)
    reasons = ['previously_inspected_data_not_unseen_evidence', 'provenance_not_independently_certified']
    if any(a['status'] == 'invalid' for a in archives):
        reasons.append('invalid_archived_report_not_used_as_verified_evidence')
    if baseline['closed_trades'] < 100:
        reasons.append('insufficient_closed_trade_sample')
    if gap_audit['missing_count']:
        reasons.append('missing_scheduled_candles_no_filling_performed')
    if gap_audit.get('unexpected_closed_session_count', 0):
        reasons.append('supplied_bars_during_expected_closed_sessions')
    if as_of is None:
        reasons.append('bar_completeness_not_checked_without_explicit_as_of')
    if baseline['net_pnl'] <= 0:
        reasons.append('baseline_does_not_outperform_zero_return_cash')
    if result['later_cost_stress']['baseline']['net_pnl'] <= 0:
        reasons.append('baseline_cost_stress_not_profitable')
    if any(f['baseline']['net_pnl'] <= 0 for f in result['later_folds']):
        reasons.append('baseline_losing_or_flat_later_fold')
    if baseline['halted_reason']:
        reasons.append('baseline_risk_halt: ' + baseline['halted_reason'])
    result['failure_reasons'] = reasons
    return result


def build_report(data_dir='research/data', research_dir='research', datasets=None,
                 as_of=None, revision=None):
    stamp = timestamp(as_of).isoformat() if as_of is not None else None
    results = [dataset_report(d, data_dir, research_dir, stamp) for d in (DATASETS if datasets is None else datasets)]
    report = dict(schema_version=1, mode='OFFLINE_HISTORICAL_PAPER_RESEARCH',
                  status='not_validated', execution_enabled=False,
                  auto_promotion=False, selected_parameters=None, cash_fallback=True,
                  as_of=stamp, datasets=results,
                  evidence_policy=dict(pristine_holdout=False, contamination=CONTAMINATION,
                                       confidence_interval='Wilson 95% descriptive interval; trade dependence and repeated searches weaken interpretation',
                                       cash='No-trade balance held constant, zero modeled yield/inflation/custody costs',
                                       folds='Independent capital/reset per fold; fold returns do not sum to whole-period return'),
                  limitations=['No independent evidence of improved profitability or future win probability',
                               'Already-inspected datasets and archived searches are contaminated for inference',
                               'No network requests, broker calls, funded accounts or automatic strategy deployment',
                               'OHLC/assumed costs cannot reproduce real fills, swaps, corporate actions or liquidity',
                               'Archived experiments are retained in full and explicitly not recomputed by this command',
                               'Pine compilation, provider connectivity and external engine execution are separate checks'])
    if revision is not None:
        report['source_revision'] = revision
    return report


def _metric_row(label, metrics):
    def value(key):
        result = metrics.get(key)
        return 'undefined' if result is None else str(result)
    return ('| ' + label + ' | ' + ' | '.join(value(k) for k in
            ('closed_trades', 'wins', 'losses', 'net_pnl', 'return_pct', 'profit_factor', 'max_drawdown_pct')) +
            ' | ' + str(metrics.get('sample_win_rate_95pct_interval')) + ' |')


def _metric_table(lines, records):
    lines += ['| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    lines += [_metric_row(label, metrics) for label, metrics in records]
    lines.append('')


def markdown(report):
    lines = ['# BROBS reproducible historical paper report', '',
             '**Status: not_validated. No automatic promotion; cash fallback preserved.**', '',
             'All periods were previously inspected. These are descriptive simulations, not independent evidence of future profitability.', '',
             'Explicit as-of: ' + str(report['as_of']) + '. No wall-clock timestamp is used.']
    if 'source_revision' in report:
        lines += ['', 'Source revision: `' + report['source_revision'] + '`.']
    for item in report['datasets']:
        lines += ['', '## ' + item['name'], '',
                  'Market/symbol: ' + item['market'] + '/' + item['symbol'] +
                  '. Data: **' + item['data_status'] + '**; validation: **not_validated**.', '',
                  'Input: `' + item['file'] + '`; SHA-256: `' + item.get('input_sha256', 'not_available') + '`.']
        if item['data_status'] == 'available':
            lines += ['', 'Dates: ' + item['first_bar'] + ' to ' + item['last_bar'] +
                      '; ' + str(item['dataset_rows']) + ' bars. Timestamps are bar opens.', '',
                      'Gap/completeness audit: `' + json.dumps(item['data_validation'], sort_keys=True) + '`.', '',
                      'Cost assumptions: `' + json.dumps(item['assumptions'], sort_keys=True) + '`.', '',
                      'Stress assumptions: `' + json.dumps(item['stress_assumptions'], sort_keys=True) + '`.', '',
                      '### Reused later period', '', item['later']['first_bar'] + ' to ' + item['later']['last_bar'] + '.', '']
            records = [(name, item['later'][name]) for name in ('baseline', 'sma', 'cash')]
            records += [(name + ' cost stress', item['later_cost_stress'][name]) for name in ('baseline', 'sma', 'cash')]
            _metric_table(lines, records)
            for group in ('training_folds', 'later_folds'):
                lines += ['### ' + group.replace('_', ' ').title(), '',
                          'Each fold resets capital; earlier bars provide warm-up only.', '']
                for i, fold in enumerate(item[group], 1):
                    lines += ['Fold ' + str(i) + ': ' + fold['first_bar'] + ' to ' + fold['last_bar'] + '.', '']
                    _metric_table(lines, [(n, fold[n]) for n in ('baseline', 'sma', 'cash')])
            lines += ['Before/after archived baseline: `' + json.dumps(item['before_after_baseline'], sort_keys=True) + '`.', '',
                      'Baseline loss reasons: `' + json.dumps(item['later']['baseline']['loss_reasons'], sort_keys=True) + '`.']
        lines += ['', 'Failure/limitation reasons: ' + '; '.join(item['failure_reasons']) + '.', '',
                  '### Archived experiments — not recomputed', '',
                  'All predeclared candidates are retained in JSON; the table below includes every available candidate phase. No winners-only filter is applied.', '']
        for archive in item['archived_experiments']:
            lines += ['#### ' + archive['file'], '',
                      'Status: ' + archive['status'] + '; SHA-256: `' + archive.get('sha256', 'not_available') + '`.']
            payload = archive.get('payload', {})
            records = []
            for i, candidate in enumerate(payload.get('candidates', []), 1):
                label = str(i) + ' ' + json.dumps(candidate.get('parameters', {}), sort_keys=True)
                if 'validation' in candidate:
                    records.append((label + ' training', candidate['validation']))
                for j, fold in enumerate(candidate.get('validation_folds', []), 1):
                    records.append((label + ' training fold ' + str(j), fold))
                if 'cost_stress' in candidate:
                    records.append((label + ' training stress', candidate['cost_stress']))
            for candidate in payload.get('fixed_later_comparisons', []):
                records.append((json.dumps(candidate['parameters'], sort_keys=True) + ' reused later', candidate['later_period']))
            for key in ('baseline', 'later_period', 'cost_stress', 'fixed_later', 'fixed_cost_stress', 'selected_later', 'selected_later_stress'):
                if key in payload and isinstance(payload[key], dict) and 'closed_trades' in payload[key]:
                    records.append((key, payload[key]))
            if records:
                lines.append('')
                _metric_table(lines, records)
            comparisons = archive.get('phase_comparisons', [])
            if comparisons:
                lines += ['Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.', '',
                          '| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |',
                          '| --- | ---: | ---: | ---: | ---: | --- |']
                for comparison in comparisons:
                    cash = comparison['cash_comparison']
                    baseline = comparison['baseline_comparison']
                    lines.append('| ' + comparison['metric_path'] + ' | ' + str(cash['net_pnl_delta']) +
                                 ' | ' + str(cash['return_pct_delta']) + ' | ' + str(baseline.get('net_pnl_delta', 'not_available')) +
                                 ' | ' + str(baseline.get('return_pct_delta', 'not_available')) + ' | ' + baseline['status'] + ' |')
                lines.append('')
            lines.append('')
    lines += ['## Limitations', ''] + ['- ' + value for value in report['limitations']]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', default='research/data')
    parser.add_argument('--research-dir', default='research')
    parser.add_argument('--csv', help='Optional single local CSV; requires market and symbol')
    parser.add_argument('--market', choices=BOOKS)
    parser.add_argument('--symbol')
    parser.add_argument('--interval-seconds', type=int)
    parser.add_argument('--provenance', help='Optional local normalized CSV provenance manifest')
    parser.add_argument('--as-of', help='Explicit aware timestamp used for last-bar completeness')
    parser.add_argument('--revision', help='Explicit immutable source revision for the report')
    parser.add_argument('--output-json', required=True)
    parser.add_argument('--output-markdown', required=True)
    parser.add_argument('--require-all-data', action='store_true', help='Exit nonzero if any input is absent/invalid; still write reports')
    args = parser.parse_args(argv)
    datasets = None
    if args.csv:
        if not args.market or not args.symbol:
            parser.error('--csv requires --market and --symbol')
        path = Path(args.csv)
        args.data_dir = str(path.parent)
        provenance_name = args.provenance
        if provenance_name:
            provenance_name = str(Path(provenance_name).resolve())
        datasets = [Dataset(path.stem, args.market, args.symbol, path.name,
                            args.interval_seconds or (86400 if args.market == 'stock' else 3600),
                            provenance_name)]
    elif any((args.market, args.symbol, args.interval_seconds, args.provenance)):
        parser.error('--market/--symbol/--interval-seconds/--provenance require --csv')
    try:
        report = build_report(args.data_dir, args.research_dir, datasets, args.as_of, args.revision)
    except ValueError as exc:
        parser.error(str(exc))
    for path, content in ((args.output_json, json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + '\n'),
                          (args.output_markdown, markdown(report))):
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
    print(json.dumps(dict(status=report['status'], available=sum(d['data_status'] == 'available' for d in report['datasets']),
                          unavailable_or_invalid=sum(d['data_status'] != 'available' for d in report['datasets']),
                          cash_fallback=True), sort_keys=True))
    return int(args.require_all_data and any(d['data_status'] != 'available' for d in report['datasets']))


if __name__ == '__main__':
    raise SystemExit(main())
