# BROBS loss-screen experiment — failed hypothesis, 31 October 2026

**Status: no performance improvement demonstrated. No promotion. Paper-only.**
Source run: https://github.com/jakeharvey162-source/Brobs/actions/runs/41192667648
Code: `brobs/independent_validation.py` in draft PR #6.
The base EURUSD dataset has 3,162 hourly observations and the later 30% holds 949 bars. This is **previously inspected** data, not a new out-of-sample evaluation.

## Hypothesis and methodology

A training-only diagnostic rule (at least eight prior trades in a regime, more losses than wins, and negative net closed-trade P&L) flags loss-prone market regimes. An offline shadow variant preserves the baseline forex decision function, prices, costs, and `FXBook` risk engine, but abstains from new entries in those regimes. Existing position exits and protective handling cannot be vetoed. Nothing is modified in default trading, live connectors or reference artifacts.

The earlier training segment yielded 60 completed trades, 9 winners, and the flagged regimes `down/ordinary` and `up/ordinary`. The later shadow run vetoed **358 new-entry signals**. These are candidate signals, **not 358 actual trades**.

## Previously inspected later EURUSD comparison

| Measure | Original baseline | Shadow regime filter | Higher-cost baseline | Higher-cost shadow |
|---|---:|---:|---:|---:|
| Closed trades | 28 | 4 | 28 | 4 |
| Wins | 11 | 0 | 11 | 0 |
| Losses | 17 | 4 | 17 | 4 |
| Breakeven | 0 | 0 | 0 | 0 |
| Observed win rate | 39.29% | 0.00% | 39.29% | 0.00% |
| Net P&L (USD, initial 10,000) | +29.2294 | -6.9578 | +16.6263 | -8.7872 |
| Net return | +0.2923% | -0.0696% | +0.1663% | -0.0879% |
| Max drawdown | 0.1906% | 0.0908% | 0.2134% | 0.1000% |
| Profit factor | 1.682 | 0 | 1.328 | 0 |

**Outcome: FAIL.** The screen reduced trade count and maximum drawdown but changed a small positive baseline return into a loss, even before stressing costs. The screened sample of four trades cannot justify any general win-rate statement. A lower drawdown alone is not evidence of a superior return.

The original reference and the separate multi-market trend-study report must not be conflated. Forex trend study was +0.2810% (28, 11/17), AAPL study was +3.9589% (8, 6/2), BTC/USDT study was -1.2204% (55, 15/40); 30 searched training candidates produced no eligible replacement. USD and USDT returns cannot be summed to manufacture combined profitability.

## Costs, provenance and limitations

Normal FX spread=0.00015; stressed spread=0.00030 with commission_fraction=0.00005. Baseline slippage_fraction=0.00005 remains unchanged. The results include spread, slippage and commission through the paper fill model, but do **not** include an individually audited realized cost ledger, historical venue quotes, financing swaps, liquidity/partial fills, or market impact.

The public EURUSD candles are vendor-sourced and their exact original timestamp/content quality has not been independently certified. The optional archived news CSV was **not supplied** (0 externally verified historical events). Paper replay cannot reliably reconstruct market reactions to unannounced headlines. The BTC raw historical archive is not checked into this repository, so a fresh independent end-to-end crypto result was **not** run here. AAPL data is old and unadjusted.

## Software verification, not profitability verification

GitHub Actions PR run #41192667648 completed successfully: **226 unit/regression tests on Python 3.11 and 226 on 3.12**, plus the separate research-determinism job. The same run independently executed the historical loss report and this shadow comparison. Latest PR runs should be checked again after subsequent edits; archived JSON artifacts will be attached by the updated CI.

**Decision: reject this loss-screen rule.** Do not tune it against the already viewed later period. Freeze any new hypothesis before collecting fresh forward paper observations, and report it whether it wins or fails. Real-money execution remains disabled.
