# Validation — 2026-10-08

## Executed locally

- **65/65 Python tests passed**, including every original test plus new FX accounting, commissions, duplicate/concurrent ticks, restart persistence, missing marks, stale/future/nonfinite quotes, unsupported account currencies, excessive spread, pause, stops, daily halts and readonly HTTP tests.
- End-to-end fixture path: practice-data-shaped adapter → signals → local execution → SQLite → dashboard state. Repeat polls deduplicate.
- Actual headless Chromium: desktop rendering, 390px mobile layout, state API and Refresh passed; **zero JavaScript errors**. A detected mobile grid overflow was fixed and retested.
- Core modules compiled with Python compileall; original synthetic demo still runs.
- New synthetic demo and optional ML-veto paths run successfully with clear synthetic provenance.
- Historical input: 3,162 vendor-supplied EURUSD H1 bars. Chronological holdout: 949 bars, 2026-08-03 08:00 UTC through 2026-09-25 20:00 UTC. No parameters optimized on holdout.
- Actual Backtrader 1.9.78.123 reference engine ran; optional sklearn research ran.

## Historical result, not a prediction

| Strategy | Closed trades | Wins / losses | Win rate | Return | Max observed drawdown |
| --- | ---: | ---: | ---: | ---: | ---: |
| BROBS multi-agent | 28 | 11 / 17 | 39.29% | +0.2923% | 0.1906% |
| SMA in same simulator | 52 | 17 / 35 | 32.69% | +0.2517% | 0.2293% |
| Optional Backtrader SMA baseline | 48 | 17 / 31 | 35.42% | +0.2950% | 0.3642% |
| Cash | 0 | — | undefined | 0% | 0% |

BROBS's sample loss rate is 60.71%; wins/losses ratio 0.647; profit factor 1.682. Its larger winners offset more losing trades in this sample. Approximate sample win-rate interval: 23.57–57.59%, with independence assumptions that may not hold.

Higher-cost stress: +0.1663% return, profit factor 1.328. The three holdout subperiod returns were +0.1193%, **−0.0272%**, +0.1811%. These are very small returns; unmodeled funding costs could erase them. Fixed assumed spread, slippage and stop-first intrabar handling are documented in JSON. Backtrader's bracket/cost rules differ: do not infer engine or strategy superiority from that row.

ML: 50.74% chronological held-out direction accuracy versus 53.38% majority baseline. Recent 200-bar model accuracy: 45.61% versus 54.39% baseline; its vote abstained. The ML variant has no trading-performance claim.

## Not validated / not completed

No real credentialed OANDA practice session was available. Broker data connectivity is implemented and fixture-tested, but provider-level integration remains unverified. No OANDA paper orders are submitted. No real-money endpoints exist. No sustained forward-paper run, multi-vendor replication, swaps, liquidity/partial fills, cross-currency P&L or broker margin/liquidation model. Public hosting/authentication and a production operations review are not complete.

## Readiness interpretation

The **local paper application is usable and tested** under the documented limited scope. Its live provider connectivity and trading edge are not established. There is no defensible basis for calling the full autonomous multi-market product “90% ready,” or saying it beats proven trading systems. Test-suite pass rate is 100%; that is not a readiness or win-rate percentage.

## Reproduce

Follow the root README. For browser checks, install Playwright separately, start the dashboard, and set `BROBS_DASHBOARD_URL` to its localhost URL before running `node scripts/browser-check.cjs`. Core operation has no Node dependency. CI includes Python tests, demos and the historical/Backtrader research runs.
