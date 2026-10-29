# Reproduce and review the offline research audit

This implements the offline evaluation work in [issue #5](https://github.com/jakeharvey162-source/Brobs/issues/5),
starting from merged main `16dfaf2a39fdf24ec9901ebdc3ef56edf904958a`.
It changes data validation and descriptive diagnostics. It does not change strategy
parameters, risk budgets, broker gateways, order routing or deployment.

## Reproduce the report

Use the existing checkout on the PR branch, Python 3.11 or 3.12, and a separate virtual
environment. The pinned validation file includes optional pandas, scikit-learn and
Backtrader so the full local suite can execute without dependency-related skips.
Core paper simulation remains standard-library-only.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-validation.txt
python -m pip check
python -m unittest discover -s tests -v
python -m brobs.research_report --as-of 2026-10-29T00:00:00+00:00 --output-json /tmp/offline-report.json --output-markdown /tmp/offline-report.md
diff research/offline-report.json /tmp/offline-report.json
diff research/offline-report.md /tmp/offline-report.md
python -m brobs.loss_lab --csv research/data/EURUSD_1h.csv --output /tmp/loss-report.json
```

Run from the repository root. Both report diffs should be empty. No command above
fetches market prices or news, accesses an account, places an order or selects a
strategy for execution. Package installation is separate from the offline simulations.
The existing `.github/workflows/tests.yml` exercises both supported interpreters,
all existing demos and research commands, and the deterministic report comparisons.
Test logs and report outputs are uploaded as CI artifacts even when a check fails.

The command uses a fixed as-of time for bar-completeness checks; it never reads the
wall clock. Omit `--as-of` only if an explicit `not_checked_no_as_of` limitation is
acceptable. `--revision <immutable-sha>` optionally adds an explicit source revision;
omit it for byte comparison with the sample. The enclosing Git commit identifies
the checked-in implementation and the pinned dependency file. Changing data,
assumptions or archived experiment files must change the recorded hashes/output.

For a separate locally supplied dataset:

```bash
python -m brobs.research_report --csv /path/to/BTCUSDT_1h.csv --market crypto --symbol BTC_USDT --interval-seconds 3600 --as-of 2026-10-29T00:00:00+00:00 --output-json /tmp/btc-report.json --output-markdown /tmp/btc-report.md
```

An optional `--provenance /path/to/manifest.json` supplies recorded source metadata.
`--require-all-data` returns a nonzero exit code for absent or invalid inputs while
still writing the report. Ordinary report generation can succeed while explicitly
reporting unavailable data; that exit status does not mean trading is validated.

## What the report compares

Fresh local replays cover the bundled EURUSD hourly and AAPL daily data. Each has
fixed chronological 30/50/70 percent boundaries, two earlier diagnostic folds,
three later folds, the existing fixed baseline, a simple SMA comparator, a
no-trade cash comparator and higher-cost stress. Every fold uses a fresh paper
ledger with earlier candles used only as indicator warm-up. Fold returns therefore
do not sum to the whole later-period return.

JSON and Markdown record dates, input SHA-256, provenance metadata, trade counts,
wins/losses, net P&L, return, profit factor, drawdown, costs, descriptive Wilson
intervals and rejection/limitation reasons. Cash has zero modeled yield, costs and
drawdown and an undefined win rate/profit factor. It is not treated as a winning trade.

Every declared archived experiment is retained, including failed candidates and
cost stresses. Archived results are labelled `archived_not_recomputed`; their
report hashes identify the exact evidence. They are not passed off as newly run
backtests or independently verified candles. Missing comparable-phase evidence is
explicit; a candidate's training return must not be compared with a baseline's
later return. Matching historical metrics is not evidence of a new advantage.

All checked-in samples and searches have already been inspected. The reports retain
`not_validated`, `selected_parameters=null`, `cash_fallback=true` and
`auto_promotion=false`. A positive historical return, high observed win rate or
software test pass cannot override those fields. No optimization target or
parameter change was introduced.

## Confirmed bugs and safeguards

- CSV and direct replay paths validate UTC-normalized chronological order and
  finite OHLC values; CSVs require volume, while the existing price-only replay
  callback API remains supported. Any supplied volume is validated.
- Duplicate instants represented with different timezone offsets are rejected.
  Naive timestamps require explicit `allow_naive_utc=True`; no implicit timezone
  assumption is made by the default loader.
- Explicit interval/as-of validation rejects incomplete bars and missing scheduled
  candles. Gap audits count and disclose gaps without interpolation or forward filling.
  Supplied holiday/weekend candles are separately counted and rejected by strict
  calendar validation; daily New York session dates remain aligned across DST.
  Report replays on gapped inputs remain descriptive and explicitly not validated.
- Forex calendar checks model the New York Friday 17:00–Sunday 17:00 weekend;
  stock checks cover daily sessions and recurring US holidays. These are limited
  calendars, not certified provider/exchange calendars or corporate-action checks.
- Replay signal callbacks receive preceding candles only, before the execution
  bar. A regression test changes the execution/future bar and checks that the
  earlier decision cannot change. Entry regimes require the candle to have closed,
  including for entries between hourly bar opens.
- Archived news must have timezone-aware publication and actual availability
  times. Both must precede the entry and be fresh; late ingestion cannot revive
  an old publication. Source URLs and local metadata do not certify truth.
- Loss-lab candle/news indices are built once per analysis. Per-trade lookup is
  logarithmic plus a fixed 101-candle statistics window, replacing repeated full
  history scans. Structural tests check index reuse without fragile speed thresholds.
  Calendar expansion has a total work bound and diagnostic lists are capped.
  The existing replay still deserializes past trades through paper-book snapshots;
  long histories can require superlinear work. No end-to-end linear-time claim is made.
- `loss_reasons` now counts losing trades only; `exit_reasons` separately counts
  all exits, and breakeven outcomes remain separate. This is a descriptive schema
  correction, not a change to trade fills or selection.

## Before and after

An immutable Git archive of merged main was checked against all source blobs
before and after the baseline run. Its full suite had 217 passing tests on both
Python 3.11.17 and 3.12.14, with zero failures, errors or skips. Every existing CI
command and saved research comparison also passed.

EURUSD input SHA-256:
`72ed2b3dba3a2b5fc500cf802a6c3f6dce0eea69629a39965edbea72719a4957`.
The later sample contains 949 of 3,162 hourly bars, from 2026-08-03 08:00 UTC to
2026-09-25 20:00 UTC. It is already inspected, not a pristine holdout.

| EURUSD fixed baseline | Merged main before | PR after |
| --- | ---: | ---: |
| Closed trades | 28 | 28 |
| Wins / losses | 11 / 17 | 11 / 17 |
| Observed win rate | 39.29% | 39.29% |
| Net simulated P&L | 29.2294 USD | 29.2294 USD |
| Return | +0.2923% | +0.2923% |
| Profit factor | 1.682 | 1.682 |
| Max observed drawdown | 0.1906% | 0.1906% |
| Descriptive 95% win interval | 23.57–57.59% | 23.57–57.59% |
| Higher-cost return | +0.1663% | +0.1663% |
| No-trade cash return | 0% | 0% |

The issue's +0.281% return / PF 1.645 do not match this exact merged-main
implementation and input hash. They were not used as replacement test expectations.
The PR preserves the measured current baseline; it claims no improvement in returns.
See the generated report for AAPL, comparators, all folds and archived experiments.

## Separate Pine compilation evidence

The unchanged `tradingview/BROBS_COUNCIL.pine` SHA-256 is
`ba2466c38e4bd3385a6bd48088ba67e5e65b37698aed3495761ca757b96fc4ab`.
An actual attempt to open `https://www.tradingview.com/chart/` returned proxy
CONNECT HTTP 403 before Pine Editor could load. **Compilation is not verified.**
The source-contract Python tests pass, but they are not Pine compiler evidence.
No unofficial parser/transpiler was substituted. The captured result is in
`research/verification/pine-compilation.json`.

To complete this check with authorized TradingView access:

1. Open the official chart and create a new Pine Editor indicator.
2. Paste the exact source at the PR revision and verify the source hash above.
3. Select Add to chart; record the exact compiler result or error line/message.
4. Save a screenshot, symbol, timeframe, date, source revision and browser details.
5. Check current-bar waiting, invalid fast/slow settings and the read-only/no-orders
   display. Record this separately from Python CI.

The initial required domain is `www.tradingview.com`; additional official editor
dependencies cannot be established until that page is accessible. No compiler
error was available to justify changing the Pine source.

## Remaining verification limits

- Three crypto CSVs are absent: BTC hourly, extended BTC hourly and ETH hourly.
  Their provenance manifests and archived reports remain visible; no synthetic bars
  were substituted. Those fresh historical runs are `not_available`.
- Recorded vendor hashes prove byte integrity only. Provenance, revised data,
  corporate actions, calendars and news authenticity are not independently certified.
- OHLC execution uses assumed costs, next-bar fills, stop-first ambiguous bars and
  final liquidation. It omits swaps, funding, liquidity, partial fills and accurate
  exchange execution. Daily stock labels are not an intraday session/execution model.
- The small EURUSD sample and reused searches cannot establish a reliable win
  probability. Confidence intervals assume independence that trades may violate.
- OANDA, Alpaca, xAI, funded accounts, broker/exchange fills and automatic strategy
  deployment are outside this work. Existing fixture tests do not verify providers.
- GitHub API access returned network-policy HTTP 403. Git read access works; API
  access and branch-specific CI/PR creation must be reported separately from local tests.
  The public Actions page showed merged-main run #99 successful at
  <https://github.com/jakeharvey162-source/Brobs/actions/runs/40920262650>.

## Review order

1. Read this scope and before/after comparison, then inspect the historical validator
   and regression tests.
2. Review loss-lab timing, index reuse and the corrected descriptive exit counts.
3. Review the report implementation and its no-network/determinism/fallback tests.
4. Regenerate both outputs, compare byte-for-byte, and inspect all failed/unavailable
   evidence alongside the positive results. Generated reports are not hand-edited.
5. Check both Python CI jobs and their uploaded artifacts at the PR's exact commit.
   Complete the separate official Pine Editor check before claiming compilation.
