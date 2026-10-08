# Win-rate improvement attempt — 8 October 2026

**A reliable 70–80% win rate was not achieved.** A training-selected candidate briefly exceeded 70%, then failed the later-period and cost checks. The existing default is retained. TradingView uses that existing strategy, not the failed candidate.

Twelve mean-reversion variants were tested: 20/40-bar windows, 1.5/2/2.5 standard-deviation entry thresholds, 0.2/0.4% stop distances, and a fixed 1:1 target/stop. There is no leverage and no martingale. The last 40% of the first 70% of the CSV was used for candidate validation. Selection required at least 40 closed trades, positive net P/L, profit factor >1 and drawdown <2%, then ranked eligible candidates by validation win rate. None of the final 30% of bars was used in that selection function.

The chosen parameters were 20 bars, 1.5 deviations, 0.4% stop and 1:1 target/stop.

| Measurement | Closed trades | Wins / losses | Win rate | Profit factor | Net return |
|---|---:|---:|---:|---:|---:|
| Candidate validation | 44 | 31 / 13 | 70.45% | 1.472 | +0.3586% |
| Later period, Aug 3–Sep 25 | 37 | 17 / 20 | 45.95% | 0.447 | −0.5783% |
| Later period, higher costs | 39 | 16 / 23 | 41.03% | 0.346 | −0.8073% |
| Existing default, same later period | 28 | 11 / 17 | 39.29% | 1.682 | +0.2923% |

The candidate's later-period win rate was higher than the default's, but its losses outweighed its wins. Higher win rate alone did not improve the app's trading performance. The later-period sample interval was 31.04–61.62%; this interval does not account for candidate-selection bias or establish future odds. Folds and all candidate metrics are in `research/reversion-evaluation.json`.

This is exploratory evidence: this later period was already examined in an earlier default-strategy benchmark. It cannot be relabeled pristine unseen data. The next valid confirmation step is fresh forward paper trading with frozen parameters, more trades, other pairs/market regimes, and broker-matched costs. Swaps/financing are not modeled. One vendor's EURUSD hourly sample is insufficient to prove a persistent edge. No 80% strategy has been validated.

Reproduce locally (Python standard library only):

```sh
python -m brobs.fx_optimize --csv research/data/EURUSD_1h.csv --output research/reversion-evaluation.json
python -m unittest discover -s tests -q
```

The optimizer writes a report; it does not alter the runner's default, stored risk settings, or open positions. Pine compilation and actual account/feed checks remain to be done in TradingView. See `docs/TRADINGVIEW.md` for installation and alerts.
