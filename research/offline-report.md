# BROBS reproducible historical paper report

**Status: not_validated. No automatic promotion; cash fallback preserved.**

All periods were previously inspected. These are descriptive simulations, not independent evidence of future profitability.

Explicit as-of: 2026-10-29T00:00:00+00:00. No wall-clock timestamp is used.

## eurusd-hourly

Market/symbol: forex/EUR_USD. Data: **available**; validation: **not_validated**.

Input: `EURUSD_1h.csv`; SHA-256: `72ed2b3dba3a2b5fc500cf802a6c3f6dce0eea69629a39965edbea72719a4957`.

Dates: 2026-03-26T03:00:00+00:00 to 2026-09-25T20:00:00+00:00; 3162 bars. Timestamps are bar opens.

Gap/completeness audit: `{"calendar_status": "no_issues_detected_by_limited_calendar", "completeness": "passed", "gap_audit": {"calendar": "forex_new_york_17_weekend", "calendar_limitation": "Only New York Friday 17:00 to Sunday 17:00 weekend closures; provider holidays are not certified", "expected_closures": 1248, "interval_seconds": 3600, "missing_count": 0, "missing_timestamps_sample": [], "unexpected_closed_session_count": 0, "unexpected_closed_session_timestamps_sample": []}, "gap_handling": "No filling/interpolation; descriptive replay retains supplied observations", "structure": "passed"}`.

Cost assumptions: `{"account_currency": "USD", "config": {"capital": 10000, "commission_fraction": 0, "daily_loss_fraction": 0.02, "drawdown_fraction": 0.1, "max_notional_fraction": 0.2, "max_quote_age_seconds": 90, "max_spread_fraction": 0.0008, "reward_risk": 2, "risk_fraction": 0.005, "slippage_fraction": 5e-05, "stop_fraction": 0.005}, "final_position": "liquidated_at_last_close", "intrabar": "stop_first_if_stop_and_target_both_touch", "leverage": 1, "signal_fill": "previous_closed_bars_to_next_open", "spread_absolute": 0.00015, "spread_fraction": null, "unmodeled": ["swaps", "funding", "dividends", "corporate_actions", "order_book_depth", "partial_fills", "live_latency"]}`.

Stress assumptions: `{"account_currency": "USD", "config": {"capital": 10000, "commission_fraction": 5e-05, "daily_loss_fraction": 0.02, "drawdown_fraction": 0.1, "max_notional_fraction": 0.2, "max_quote_age_seconds": 90, "max_spread_fraction": 0.0008, "reward_risk": 2, "risk_fraction": 0.005, "slippage_fraction": 5e-05, "stop_fraction": 0.005}, "final_position": "liquidated_at_last_close", "intrabar": "stop_first_if_stop_and_target_both_touch", "leverage": 1, "signal_fill": "previous_closed_bars_to_next_open", "spread_absolute": 0.0003, "spread_fraction": null, "unmodeled": ["swaps", "funding", "dividends", "corporate_actions", "order_book_depth", "partial_fills", "live_latency"]}`.

### Reused later period

2026-08-03T08:00:00+00:00 to 2026-09-25T20:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 28 | 11 | 17 | 29.2294 | 0.2923 | 1.682 | 0.1906 | [23.57, 57.59] |
| sma | 52 | 17 | 35 | 25.1725 | 0.2517 | 1.314 | 0.2293 | [21.52, 46.24] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |
| baseline cost stress | 28 | 11 | 17 | 16.6263 | 0.1663 | 1.328 | 0.2134 | [23.57, 57.59] |
| sma cost stress | 52 | 17 | 35 | 1.8085 | 0.0181 | 1.019 | 0.3184 | [21.52, 46.24] |
| cash cost stress | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

### Training Folds

Each fold resets capital; earlier bars provide warm-up only.

Fold 1: 2026-05-20T15:00:00+00:00 to 2026-06-25T23:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 29 | 4 | 25 | -67.0467 | -0.6705 | 0.341 | 0.8784 | [5.5, 30.56] |
| sma | 43 | 12 | 31 | -41.4368 | -0.4144 | 0.56 | 0.752 | [16.75, 42.69] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

Fold 2: 2026-06-26T00:00:00+00:00 to 2026-08-03T07:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 31 | 5 | 26 | -94.1568 | -0.9416 | 0.117 | 1.0272 | [7.09, 32.63] |
| sma | 35 | 8 | 27 | -85.6824 | -0.8568 | 0.215 | 1.04 | [12.07, 39.02] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

### Later Folds

Each fold resets capital; earlier bars provide warm-up only.

Fold 1: 2026-08-03T08:00:00+00:00 to 2026-08-20T11:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 10 | 5 | 5 | 11.9336 | 0.1193 | 1.764 | 0.1906 | [23.66, 76.34] |
| sma | 16 | 7 | 9 | 12.4 | 0.124 | 1.508 | 0.2215 | [23.1, 66.82] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

Fold 2: 2026-08-20T12:00:00+00:00 to 2026-09-08T15:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 13 | 4 | 9 | -2.715 | -0.0272 | 0.84 | 0.1112 | [12.68, 57.63] |
| sma | 18 | 6 | 12 | 10.3169 | 0.1032 | 1.395 | 0.1345 | [16.28, 56.25] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

Fold 3: 2026-09-08T16:00:00+00:00 to 2026-09-25T20:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 6 | 2 | 4 | 18.1098 | 0.1811 | 2.366 | 0.1484 | [9.68, 70.0] |
| sma | 20 | 4 | 16 | 1.5164 | 0.0152 | 1.05 | 0.2293 | [8.07, 41.6] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

Before/after archived baseline: `{"after": {"breakeven": 0, "closed_trades": 28, "losses": 17, "max_drawdown_pct": 0.1906, "net_pnl": 29.2294, "profit_factor": 1.682, "return_pct": 0.2923, "sample_win_rate_95pct_interval": [23.57, 57.59], "win_rate_pct": 39.29, "wins": 11}, "archive_file": "eurusd-holdout.json", "archive_input_sha256": null, "archive_sha256": "20251198b5976204659d34ef8207e5a4d76b062eaef0dacb89a48ad89d34a6ee", "before": {"breakeven": 0, "closed_trades": 28, "losses": 17, "max_drawdown_pct": 0.1906, "net_pnl": 29.2294, "profit_factor": 1.682, "return_pct": 0.2923, "sample_win_rate_95pct_interval": [23.57, 57.59], "win_rate_pct": 39.29, "wins": 11}, "caveat": "A metric match is not independent data verification; costs and input digests must also be reviewed", "differences": {}, "input_identity": "not_recorded_in_legacy_report", "status": "metrics_match"}`.

Baseline loss reasons: `{"opposite_signal": 17}`.

Failure/limitation reasons: previously_inspected_data_not_unseen_evidence; provenance_not_independently_certified; insufficient_closed_trade_sample; baseline_losing_or_flat_later_fold.

### Archived experiments — not recomputed

All predeclared candidates are retained in JSON; the table below includes every available candidate phase. No winners-only filter is applied.

#### eurusd-holdout.json

Status: archived_not_recomputed; SHA-256: `20251198b5976204659d34ef8207e5a4d76b062eaef0dacb89a48ad89d34a6ee`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| cost_stress | 28 | 11 | 17 | 16.6263 | 0.1663 | 1.328 | 0.2134 | [23.57, 57.59] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| results.multi_agent | 29.2294 | 0.2923 | 0.0 | 0.0 | descriptive_same_archive_phase |
| results.sma | 25.1725 | 0.2517 | -4.0569 | -0.0406 | descriptive_same_archive_phase |
| results.cash | None | 0 | not_available | not_available | not_available |
| cost_stress | 16.6263 | 0.1663 | not_available | not_available | not_available |
| chronological_test_folds.0 | 11.9336 | 0.1193 | not_available | not_available | not_available |
| chronological_test_folds.1 | -2.715 | -0.0272 | not_available | not_available | not_available |
| chronological_test_folds.2 | 18.1098 | 0.1811 | not_available | not_available | not_available |


#### forex-strategy-evaluation.json

Status: archived_not_recomputed; SHA-256: `3f8ab435e53d48d0dc9bee2087097c1d7aa29c7bc164716d3654150c62346864`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.002, "threshold": 5} training | 19 | 9 | 10 | -0.0656 | -0.0007 | 0.994 | 0.1182 | [27.33, 68.29] |
| 2 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.004, "threshold": 5} training | 19 | 9 | 10 | 3.9737 | 0.0397 | 1.529 | 0.0778 | [27.33, 68.29] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.002, "threshold": 10} training | 41 | 17 | 24 | -12.4343 | -0.1243 | 0.66 | 0.2647 | [27.76, 56.63] |
| 4 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.004, "threshold": 10} training | 40 | 17 | 23 | -6.6652 | -0.0667 | 0.76 | 0.2085 | [28.51, 57.81] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.002, "threshold": 20} training | 79 | 37 | 42 | -49.0893 | -0.4909 | 0.46 | 0.6603 | [36.24, 57.73] |
| 6 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.004, "threshold": 20} training | 74 | 33 | 41 | -40.853 | -0.4085 | 0.483 | 0.5912 | [33.82, 55.91] |
| 7 {"family": "rsi_pullback", "reward_risk": 1.5, "stop_fraction": 0.002, "threshold": 35} training | 1 | 1 | 0 | 5.8981 | 0.059 | undefined | 0.0082 | [20.65, 100.0] |
| 8 {"family": "rsi_pullback", "reward_risk": 1.5, "stop_fraction": 0.002, "threshold": 40} training | 11 | 3 | 8 | 2.9448 | 0.0294 | 1.2 | 0.175 | [9.75, 56.57] |
| 9 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.002, "threshold": 10} training | 42 | 8 | 34 | -76.2031 | -0.762 | 0.358 | 0.8239 | [9.98, 33.3] |
| 10 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.002, "threshold": 10} training | 58 | 11 | 47 | -91.9194 | -0.9192 | 0.413 | 1.1326 | [10.93, 30.85] |
| baseline | 28 | 11 | 17 | 28.0983 | 0.281 | 1.645 | 0.1927 | [23.57, 57.59] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation | -0.0656 | -0.0007 | not_available | not_available | not_available |
| candidates.1.validation | 3.9737 | 0.0397 | not_available | not_available | not_available |
| candidates.2.validation | -12.4343 | -0.1243 | not_available | not_available | not_available |
| candidates.3.validation | -6.6652 | -0.0667 | not_available | not_available | not_available |
| candidates.4.validation | -49.0893 | -0.4909 | not_available | not_available | not_available |
| candidates.5.validation | -40.853 | -0.4085 | not_available | not_available | not_available |
| candidates.6.validation | 5.8981 | 0.059 | not_available | not_available | not_available |
| candidates.7.validation | 2.9448 | 0.0294 | not_available | not_available | not_available |
| candidates.8.validation | -76.2031 | -0.762 | not_available | not_available | not_available |
| candidates.9.validation | -91.9194 | -0.9192 | not_available | not_available | not_available |
| baseline | 28.0983 | 0.281 | 0.0 | 0.0 | descriptive_same_archive_phase |
| baseline_cost_stress | 8.8646 | 0.0886 | 0.0 | 0.0 | descriptive_same_archive_phase |


#### reversion-evaluation.json

Status: archived_not_recomputed; SHA-256: `67f28f65750dda2e68636c4d03113f0e38b0e83eafc31593875a8d0903122cc4`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"deviation": 1.5, "period": 20, "reward_risk": 1, "stop_fraction": 0.002} training | 72 | 43 | 29 | 27.0217 | 0.2702 | 1.228 | 0.3271 | [48.18, 70.28] |
| 2 {"deviation": 1.5, "period": 20, "reward_risk": 1, "stop_fraction": 0.004} training | 44 | 31 | 13 | 35.8596 | 0.3586 | 1.472 | 0.4673 | [55.78, 81.84] |
| 3 {"deviation": 2.0, "period": 20, "reward_risk": 1, "stop_fraction": 0.002} training | 48 | 27 | 21 | 17.2116 | 0.1721 | 1.21 | 0.277 | [42.27, 69.3] |
| 4 {"deviation": 2.0, "period": 20, "reward_risk": 1, "stop_fraction": 0.004} training | 29 | 19 | 10 | 17.89 | 0.1789 | 1.271 | 0.4704 | [47.34, 80.06] |
| 5 {"deviation": 2.5, "period": 20, "reward_risk": 1, "stop_fraction": 0.002} training | 31 | 18 | 13 | 16.1976 | 0.162 | 1.304 | 0.1794 | [40.77, 73.58] |
| 6 {"deviation": 2.5, "period": 20, "reward_risk": 1, "stop_fraction": 0.004} training | 22 | 10 | 12 | 1.1901 | 0.0119 | 1.017 | 0.4006 | [26.92, 65.34] |
| 7 {"deviation": 1.5, "period": 40, "reward_risk": 1, "stop_fraction": 0.002} training | 52 | 31 | 21 | 38.5767 | 0.3858 | 1.47 | 0.2595 | [46.07, 71.84] |
| 8 {"deviation": 1.5, "period": 40, "reward_risk": 1, "stop_fraction": 0.004} training | 27 | 19 | 8 | 32.5543 | 0.3255 | 1.568 | 0.3891 | [51.52, 84.15] |
| 9 {"deviation": 2.0, "period": 40, "reward_risk": 1, "stop_fraction": 0.002} training | 30 | 20 | 10 | 34.8468 | 0.3485 | 1.849 | 0.1262 | [48.78, 80.77] |
| 10 {"deviation": 2.0, "period": 40, "reward_risk": 1, "stop_fraction": 0.004} training | 20 | 13 | 7 | 29.7625 | 0.2976 | 1.524 | 0.279 | [43.29, 81.88] |
| 11 {"deviation": 2.5, "period": 40, "reward_risk": 1, "stop_fraction": 0.002} training | 19 | 13 | 6 | 25.4225 | 0.2542 | 2.033 | 0.1611 | [46.01, 84.64] |
| 12 {"deviation": 2.5, "period": 40, "reward_risk": 1, "stop_fraction": 0.004} training | 13 | 8 | 5 | 18.0435 | 0.1804 | 1.445 | 0.2911 | [35.52, 82.29] |
| later_period | 37 | 17 | 20 | -57.83 | -0.5783 | 0.447 | 0.6187 | [31.04, 61.62] |
| cost_stress | 39 | 16 | 23 | -80.7315 | -0.8073 | 0.346 | 0.8385 | [27.08, 56.58] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation | 27.0217 | 0.2702 | not_available | not_available | not_available |
| candidates.1.validation | 35.8596 | 0.3586 | not_available | not_available | not_available |
| candidates.2.validation | 17.2116 | 0.1721 | not_available | not_available | not_available |
| candidates.3.validation | 17.89 | 0.1789 | not_available | not_available | not_available |
| candidates.4.validation | 16.1976 | 0.162 | not_available | not_available | not_available |
| candidates.5.validation | 1.1901 | 0.0119 | not_available | not_available | not_available |
| candidates.6.validation | 38.5767 | 0.3858 | not_available | not_available | not_available |
| candidates.7.validation | 32.5543 | 0.3255 | not_available | not_available | not_available |
| candidates.8.validation | 34.8468 | 0.3485 | not_available | not_available | not_available |
| candidates.9.validation | 29.7625 | 0.2976 | not_available | not_available | not_available |
| candidates.10.validation | 25.4225 | 0.2542 | not_available | not_available | not_available |
| candidates.11.validation | 18.0435 | 0.1804 | not_available | not_available | not_available |
| selected.validation | 35.8596 | 0.3586 | not_available | not_available | not_available |
| later_period | -57.83 | -0.5783 | not_available | not_available | not_available |
| cost_stress | -80.7315 | -0.8073 | not_available | not_available | not_available |
| later_folds.0 | -30.1637 | -0.3016 | not_available | not_available | not_available |
| later_folds.1 | 1.2444 | 0.0124 | not_available | not_available | not_available |
| later_folds.2 | -29.2017 | -0.292 | not_available | not_available | not_available |


#### lab-forex-evaluation.json

Status: archived_not_recomputed; SHA-256: `1614e0b1bf00fd3a38d071818a34d728938af3e7165222df689027e9c369a940`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} training fold 1 | 0 | 0 | 0 | 0 | 0.0 | undefined | 0 | None |
| 1 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} training fold 2 | 0 | 0 | 0 | 0 | 0.0 | undefined | 0 | None |
| 1 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} training stress | 0 | 0 | 0 | 0 | 0.0 | undefined | 0 | None |
| 2 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 45} training fold 1 | 3 | 2 | 1 | -4.9724 | -0.0497 | 0.508 | 0.1019 | [20.77, 93.85] |
| 2 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 45} training fold 2 | 7 | 4 | 3 | -4.9492 | -0.0495 | 0.608 | 0.1528 | [25.05, 84.18] |
| 2 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 45} training stress | 10 | 6 | 4 | -16.1114 | -0.1611 | 0.348 | 0.23 | [31.27, 83.18] |
| 3 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} training fold 1 | 9 | 9 | 0 | 29.1404 | 0.2914 | undefined | 0.0452 | [70.08, 100.0] |
| 3 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} training fold 2 | 10 | 7 | 3 | 21.8598 | 0.2186 | 9.247 | 0.0501 | [39.68, 89.22] |
| 3 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} training stress | 19 | 15 | 4 | 37.7188 | 0.3772 | 8.689 | 0.0623 | [56.67, 91.49] |
| 4 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 45} training fold 1 | 24 | 20 | 4 | 20.8115 | 0.2081 | 1.853 | 0.2464 | [64.15, 93.32] |
| 4 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 45} training fold 2 | 22 | 14 | 8 | 1.9291 | 0.0193 | 1.073 | 0.2208 | [42.95, 80.27] |
| 4 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 45} training stress | 46 | 28 | 18 | -7.8581 | -0.0786 | 0.868 | 0.357 | [46.46, 73.61] |
| 5 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 40} training fold 1 | 26 | 6 | 20 | -20.5165 | -0.2052 | 0.514 | 0.2949 | [11.03, 42.05] |
| 5 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 40} training fold 2 | 25 | 7 | 18 | -16.7306 | -0.1673 | 0.585 | 0.2544 | [14.28, 47.58] |
| 5 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 40} training stress | 51 | 10 | 41 | -72.9787 | -0.7298 | 0.327 | 0.8238 | [11.02, 32.46] |
| 6 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 40} training fold 1 | 26 | 6 | 20 | -23.3044 | -0.233 | 0.442 | 0.3234 | [11.03, 42.05] |
| 6 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 40} training fold 2 | 25 | 7 | 18 | -23.9777 | -0.2398 | 0.471 | 0.3042 | [14.28, 47.58] |
| 6 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 40} training stress | 51 | 10 | 41 | -82.3082 | -0.8231 | 0.279 | 0.917 | [11.02, 32.46] |
| 7 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training fold 1 | 29 | 4 | 25 | -68.1758 | -0.6818 | 0.337 | 0.8876 | [5.5, 30.56] |
| 7 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training fold 2 | 31 | 5 | 26 | -95.35 | -0.9535 | 0.115 | 1.0388 | [7.09, 32.63] |
| 7 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training stress | 60 | 5 | 55 | -202.5195 | -2.0252 | 0.171 | 2.0254 | [3.61, 18.07] |
| 8 {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 40} training fold 1 | 6 | 3 | 3 | -0.2667 | -0.0027 | 0.948 | 0.0685 | [18.76, 81.24] |
| 8 {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 40} training fold 2 | 9 | 2 | 7 | 0.855 | 0.0085 | 1.067 | 0.125 | [6.32, 54.74] |
| 8 {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 40} training stress | 14 | 3 | 11 | -13.0803 | -0.1308 | 0.494 | 0.2522 | [7.57, 47.59] |
| 9 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training fold 1 | 24 | 12 | 12 | 9.8323 | 0.0983 | 2.307 | 0.0704 | [31.43, 68.57] |
| 9 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training fold 2 | 30 | 12 | 18 | -13.0569 | -0.1306 | 0.469 | 0.1932 | [24.59, 57.68] |
| 9 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training stress | 54 | 14 | 40 | -40.9491 | -0.4095 | 0.272 | 0.4669 | [16.12, 38.93] |
| 10 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training fold 1 | 16 | 3 | 13 | -17.4124 | -0.1741 | 0.655 | 0.4859 | [6.59, 43.01] |
| 10 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training fold 2 | 26 | 4 | 22 | -82.3236 | -0.8232 | 0.031 | 0.8638 | [6.15, 33.53] |
| 10 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training stress | 42 | 5 | 37 | -128.4896 | -1.2849 | 0.202 | 1.2933 | [5.19, 25.0] |
| {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} reused later | 2 | 2 | 0 | 1.9955 | 0.02 | undefined | 0.0147 | [34.24, 100.0] |
| {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 45} reused later | 8 | 2 | 6 | -6.151 | -0.0615 | 0.332 | 0.0921 | [7.15, 59.07] |
| {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} reused later | 10 | 6 | 4 | -20.5782 | -0.2058 | 0.349 | 0.2145 | [31.27, 83.18] |
| {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 45} reused later | 24 | 13 | 11 | -29.0822 | -0.2908 | 0.435 | 0.3146 | [35.07, 72.11] |
| {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 40} reused later | 33 | 11 | 22 | 26.528 | 0.2653 | 1.658 | 0.15 | [19.75, 50.39] |
| {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 40} reused later | 33 | 11 | 22 | 21.8659 | 0.2187 | 1.542 | 0.15 | [19.75, 50.39] |
| {"family": "trend", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} reused later | 28 | 11 | 17 | 28.0983 | 0.281 | 1.645 | 0.1927 | [23.57, 57.59] |
| {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 40} reused later | 5 | 4 | 1 | 16.1694 | 0.1617 | 74.692 | 0.0308 | [37.55, 96.38] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} reused later | 39 | 20 | 19 | 2.9083 | 0.0291 | 1.215 | 0.0735 | [36.2, 66.14] |
| {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} reused later | 20 | 7 | 13 | 7.2129 | 0.0721 | 1.212 | 0.2751 | [18.12, 56.71] |
| baseline | 28 | 11 | 17 | 28.0983 | 0.281 | 1.645 | 0.1927 | [23.57, 57.59] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation_folds.0 | 0 | 0.0 | not_available | not_available | not_available |
| candidates.0.validation_folds.1 | 0 | 0.0 | not_available | not_available | not_available |
| candidates.0.cost_stress | 0 | 0.0 | not_available | not_available | not_available |
| candidates.1.validation_folds.0 | -4.9724 | -0.0497 | not_available | not_available | not_available |
| candidates.1.validation_folds.1 | -4.9492 | -0.0495 | not_available | not_available | not_available |
| candidates.1.cost_stress | -16.1114 | -0.1611 | not_available | not_available | not_available |
| candidates.2.validation_folds.0 | 29.1404 | 0.2914 | not_available | not_available | not_available |
| candidates.2.validation_folds.1 | 21.8598 | 0.2186 | not_available | not_available | not_available |
| candidates.2.cost_stress | 37.7188 | 0.3772 | not_available | not_available | not_available |
| candidates.3.validation_folds.0 | 20.8115 | 0.2081 | not_available | not_available | not_available |
| candidates.3.validation_folds.1 | 1.9291 | 0.0193 | not_available | not_available | not_available |
| candidates.3.cost_stress | -7.8581 | -0.0786 | not_available | not_available | not_available |
| candidates.4.validation_folds.0 | -20.5165 | -0.2052 | not_available | not_available | not_available |
| candidates.4.validation_folds.1 | -16.7306 | -0.1673 | not_available | not_available | not_available |
| candidates.4.cost_stress | -72.9787 | -0.7298 | not_available | not_available | not_available |
| candidates.5.validation_folds.0 | -23.3044 | -0.233 | not_available | not_available | not_available |
| candidates.5.validation_folds.1 | -23.9777 | -0.2398 | not_available | not_available | not_available |
| candidates.5.cost_stress | -82.3082 | -0.8231 | not_available | not_available | not_available |
| candidates.6.validation_folds.0 | -68.1758 | -0.6818 | not_available | not_available | not_available |
| candidates.6.validation_folds.1 | -95.35 | -0.9535 | not_available | not_available | not_available |
| candidates.6.cost_stress | -202.5195 | -2.0252 | not_available | not_available | not_available |
| candidates.7.validation_folds.0 | -0.2667 | -0.0027 | not_available | not_available | not_available |
| candidates.7.validation_folds.1 | 0.855 | 0.0085 | not_available | not_available | not_available |
| candidates.7.cost_stress | -13.0803 | -0.1308 | not_available | not_available | not_available |
| candidates.8.validation_folds.0 | 9.8323 | 0.0983 | not_available | not_available | not_available |
| candidates.8.validation_folds.1 | -13.0569 | -0.1306 | not_available | not_available | not_available |
| candidates.8.cost_stress | -40.9491 | -0.4095 | not_available | not_available | not_available |
| candidates.9.validation_folds.0 | -17.4124 | -0.1741 | not_available | not_available | not_available |
| candidates.9.validation_folds.1 | -82.3236 | -0.8232 | not_available | not_available | not_available |
| candidates.9.cost_stress | -128.4896 | -1.2849 | not_available | not_available | not_available |
| baseline | 28.0983 | 0.281 | 0.0 | 0.0 | descriptive_same_archive_phase |
| fixed_later_comparisons.0.later_period | 1.9955 | 0.02 | -26.1028 | -0.261 | descriptive_same_archive_phase |
| fixed_later_comparisons.1.later_period | -6.151 | -0.0615 | -34.2493 | -0.3425 | descriptive_same_archive_phase |
| fixed_later_comparisons.2.later_period | -20.5782 | -0.2058 | -48.6765 | -0.4868 | descriptive_same_archive_phase |
| fixed_later_comparisons.3.later_period | -29.0822 | -0.2908 | -57.1805 | -0.5718 | descriptive_same_archive_phase |
| fixed_later_comparisons.4.later_period | 26.528 | 0.2653 | -1.5703 | -0.0157 | descriptive_same_archive_phase |
| fixed_later_comparisons.5.later_period | 21.8659 | 0.2187 | -6.2324 | -0.0623 | descriptive_same_archive_phase |
| fixed_later_comparisons.6.later_period | 28.0983 | 0.281 | 0.0 | 0.0 | descriptive_same_archive_phase |
| fixed_later_comparisons.7.later_period | 16.1694 | 0.1617 | -11.9289 | -0.1193 | descriptive_same_archive_phase |
| fixed_later_comparisons.8.later_period | 2.9083 | 0.0291 | -25.19 | -0.2519 | descriptive_same_archive_phase |
| fixed_later_comparisons.9.later_period | 7.2129 | 0.0721 | -20.8854 | -0.2089 | descriptive_same_archive_phase |


#### winrate-forex-evaluation.json

Status: archived_not_recomputed; SHA-256: `606becc950a5e55ef5e03cd30c2e59153e5d1fbc43d4a562b9f6dc1bf4ca9eb7`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 5} training fold 1 | 10 | 7 | 3 | 3.7417 | 0.0374 | 1.617 | 0.0613 | [39.68, 89.22] |
| 1 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 5} training fold 2 | 14 | 5 | 9 | -5.3425 | -0.0534 | 0.386 | 0.0931 | [16.34, 61.24] |
| 1 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 5} training stress | 24 | 6 | 18 | -17.1853 | -0.1719 | 0.316 | 0.1885 | [12.0, 44.9] |
| 2 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 5} training fold 1 | 10 | 7 | 3 | 4.322 | 0.0432 | 1.713 | 0.0613 | [39.68, 89.22] |
| 2 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 5} training fold 2 | 14 | 5 | 9 | -5.3425 | -0.0534 | 0.386 | 0.0931 | [16.34, 61.24] |
| 2 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 5} training stress | 24 | 6 | 18 | -17.006 | -0.1701 | 0.323 | 0.1867 | [12.0, 44.9] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 5} training fold 1 | 10 | 8 | 2 | 13.7318 | 0.1373 | 15.211 | 0.056 | [49.02, 94.33] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 5} training fold 2 | 14 | 5 | 9 | -3.7152 | -0.0372 | 0.475 | 0.0768 | [16.34, 61.24] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 5} training stress | 24 | 7 | 17 | -6.7829 | -0.0678 | 0.634 | 0.1606 | [14.91, 49.17] |
| 4 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 5} training fold 1 | 10 | 8 | 2 | 13.7318 | 0.1373 | 15.211 | 0.056 | [49.02, 94.33] |
| 4 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 5} training fold 2 | 14 | 5 | 9 | -3.7152 | -0.0372 | 0.475 | 0.0768 | [16.34, 61.24] |
| 4 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 5} training stress | 24 | 7 | 17 | -6.7829 | -0.0678 | 0.634 | 0.1606 | [14.91, 49.17] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 10} training fold 1 | 24 | 11 | 13 | -0.0386 | -0.0004 | 0.997 | 0.0988 | [27.89, 64.93] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 10} training fold 2 | 31 | 12 | 19 | -18.6212 | -0.1862 | 0.422 | 0.2373 | [23.73, 56.18] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 10} training stress | 55 | 13 | 42 | -54.6189 | -0.5462 | 0.205 | 0.5961 | [14.37, 36.35] |
| 6 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 10} training fold 1 | 24 | 11 | 13 | 0.5414 | 0.0054 | 1.043 | 0.0988 | [27.89, 64.93] |
| 6 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 10} training fold 2 | 31 | 12 | 19 | -17.4674 | -0.1747 | 0.458 | 0.2373 | [23.73, 56.18] |
| 6 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 10} training stress | 55 | 13 | 42 | -53.6911 | -0.5369 | 0.219 | 0.5943 | [14.37, 36.35] |
| 7 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 10} training fold 1 | 24 | 12 | 12 | 9.8323 | 0.0983 | 2.307 | 0.0704 | [31.43, 68.57] |
| 7 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 10} training fold 2 | 30 | 12 | 18 | -13.0569 | -0.1306 | 0.469 | 0.1932 | [24.59, 57.68] |
| 7 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 10} training stress | 54 | 14 | 40 | -40.9491 | -0.4095 | 0.272 | 0.4669 | [16.12, 38.93] |
| 8 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training fold 1 | 24 | 12 | 12 | 9.8323 | 0.0983 | 2.307 | 0.0704 | [31.43, 68.57] |
| 8 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training fold 2 | 30 | 12 | 18 | -13.0569 | -0.1306 | 0.469 | 0.1932 | [24.59, 57.68] |
| 8 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training stress | 54 | 14 | 40 | -40.9491 | -0.4095 | 0.272 | 0.4669 | [16.12, 38.93] |
| 9 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 20} training fold 1 | 46 | 22 | 24 | -21.2681 | -0.2127 | 0.527 | 0.3172 | [34.12, 61.86] |
| 9 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 20} training fold 2 | 54 | 19 | 35 | -54.136 | -0.5414 | 0.259 | 0.5855 | [23.82, 48.52] |
| 9 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 20} training stress | 102 | 23 | 79 | -145.1051 | -1.4511 | 0.129 | 1.4829 | [15.52, 31.57] |
| 10 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 20} training fold 1 | 46 | 22 | 24 | -21.2681 | -0.2127 | 0.527 | 0.3172 | [34.12, 61.86] |
| 10 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 20} training fold 2 | 54 | 19 | 35 | -52.9862 | -0.5299 | 0.275 | 0.5855 | [23.82, 48.52] |
| 10 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 20} training stress | 102 | 23 | 79 | -144.3612 | -1.4436 | 0.133 | 1.4829 | [15.52, 31.57] |
| 11 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 20} training fold 1 | 44 | 22 | 22 | -2.3283 | -0.0233 | 0.921 | 0.1367 | [35.83, 64.17] |
| 11 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 20} training fold 2 | 52 | 17 | 35 | -51.0907 | -0.5109 | 0.192 | 0.5663 | [21.52, 46.24] |
| 11 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 20} training stress | 96 | 20 | 76 | -119.6225 | -1.1962 | 0.132 | 1.2355 | [13.91, 30.0] |
| 12 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 20} training fold 1 | 44 | 22 | 22 | -2.3283 | -0.0233 | 0.921 | 0.1367 | [35.83, 64.17] |
| 12 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 20} training fold 2 | 52 | 17 | 35 | -51.0907 | -0.5109 | 0.192 | 0.5663 | [21.52, 46.24] |
| 12 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 20} training stress | 96 | 20 | 76 | -119.6225 | -1.1962 | 0.132 | 1.2355 | [13.91, 30.0] |
| 13 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 35} training fold 1 | 71 | 35 | 36 | -45.0594 | -0.4506 | 0.39 | 0.4949 | [38.0, 60.66] |
| 13 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 35} training fold 2 | 74 | 29 | 45 | -57.7195 | -0.5772 | 0.411 | 0.6108 | [28.86, 50.58] |
| 13 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 35} training stress | 148 | 31 | 117 | -206.4162 | -2.0642 | 0.162 | 2.0765 | [15.17, 28.2] |
| 14 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 35} training fold 1 | 71 | 35 | 36 | -45.0594 | -0.4506 | 0.39 | 0.4949 | [38.0, 60.66] |
| 14 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 35} training fold 2 | 74 | 29 | 45 | -50.4712 | -0.5047 | 0.485 | 0.5527 | [28.86, 50.58] |
| 14 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 35} training stress | 148 | 31 | 117 | -200.4539 | -2.0045 | 0.187 | 2.0243 | [15.17, 28.2] |
| 15 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 35} training fold 1 | 66 | 34 | 32 | -21.9022 | -0.219 | 0.592 | 0.2635 | [39.71, 63.15] |
| 15 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 35} training fold 2 | 69 | 24 | 45 | -61.9842 | -0.6198 | 0.28 | 0.6556 | [24.62, 46.55] |
| 15 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 35} training stress | 135 | 25 | 110 | -176.6059 | -1.7661 | 0.138 | 1.7857 | [12.87, 25.91] |
| 16 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} training fold 1 | 66 | 34 | 32 | -21.9022 | -0.219 | 0.592 | 0.2635 | [39.71, 63.15] |
| 16 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} training fold 2 | 69 | 24 | 45 | -61.9842 | -0.6198 | 0.28 | 0.6556 | [24.62, 46.55] |
| 16 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} training stress | 135 | 25 | 110 | -176.6059 | -1.7661 | 0.138 | 1.7857 | [12.87, 25.91] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 5} reused later | 19 | 10 | 9 | -1.1924 | -0.0119 | 0.89 | 0.056 | [31.71, 72.67] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 5} reused later | 19 | 10 | 9 | -1.1924 | -0.0119 | 0.89 | 0.056 | [31.71, 72.67] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 5} reused later | 19 | 10 | 9 | 3.7019 | 0.037 | 1.622 | 0.0447 | [31.71, 72.67] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 5} reused later | 19 | 10 | 9 | 3.7019 | 0.037 | 1.622 | 0.0447 | [31.71, 72.67] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 10} reused later | 39 | 20 | 19 | -0.7655 | -0.0077 | 0.955 | 0.0735 | [36.2, 66.14] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 10} reused later | 39 | 20 | 19 | -0.7655 | -0.0077 | 0.955 | 0.0735 | [36.2, 66.14] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 10} reused later | 39 | 20 | 19 | 2.9083 | 0.0291 | 1.215 | 0.0735 | [36.2, 66.14] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} reused later | 39 | 20 | 19 | 2.9083 | 0.0291 | 1.215 | 0.0735 | [36.2, 66.14] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 20} reused later | 74 | 34 | 40 | -21.8329 | -0.2183 | 0.571 | 0.281 | [35.07, 57.22] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 20} reused later | 74 | 34 | 40 | -21.8329 | -0.2183 | 0.571 | 0.281 | [35.07, 57.22] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 20} reused later | 72 | 33 | 39 | -19.5748 | -0.1957 | 0.576 | 0.2824 | [34.83, 57.26] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 20} reused later | 72 | 33 | 39 | -19.5748 | -0.1957 | 0.576 | 0.2824 | [34.83, 57.26] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.0025, "threshold": 35} reused later | 111 | 55 | 56 | -54.7568 | -0.5476 | 0.391 | 0.6042 | [40.42, 58.71] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 35} reused later | 111 | 55 | 56 | -54.7568 | -0.5476 | 0.391 | 0.6042 | [40.42, 58.71] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.005, "threshold": 35} reused later | 109 | 54 | 55 | -52.511 | -0.5251 | 0.384 | 0.6143 | [40.33, 58.78] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 35} reused later | 109 | 54 | 55 | -52.511 | -0.5251 | 0.384 | 0.6143 | [40.33, 58.78] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation_folds.0 | 3.7417 | 0.0374 | not_available | not_available | not_available |
| candidates.0.validation_folds.1 | -5.3425 | -0.0534 | not_available | not_available | not_available |
| candidates.0.cost_stress | -17.1853 | -0.1719 | not_available | not_available | not_available |
| candidates.1.validation_folds.0 | 4.322 | 0.0432 | not_available | not_available | not_available |
| candidates.1.validation_folds.1 | -5.3425 | -0.0534 | not_available | not_available | not_available |
| candidates.1.cost_stress | -17.006 | -0.1701 | not_available | not_available | not_available |
| candidates.2.validation_folds.0 | 13.7318 | 0.1373 | not_available | not_available | not_available |
| candidates.2.validation_folds.1 | -3.7152 | -0.0372 | not_available | not_available | not_available |
| candidates.2.cost_stress | -6.7829 | -0.0678 | not_available | not_available | not_available |
| candidates.3.validation_folds.0 | 13.7318 | 0.1373 | not_available | not_available | not_available |
| candidates.3.validation_folds.1 | -3.7152 | -0.0372 | not_available | not_available | not_available |
| candidates.3.cost_stress | -6.7829 | -0.0678 | not_available | not_available | not_available |
| candidates.4.validation_folds.0 | -0.0386 | -0.0004 | not_available | not_available | not_available |
| candidates.4.validation_folds.1 | -18.6212 | -0.1862 | not_available | not_available | not_available |
| candidates.4.cost_stress | -54.6189 | -0.5462 | not_available | not_available | not_available |
| candidates.5.validation_folds.0 | 0.5414 | 0.0054 | not_available | not_available | not_available |
| candidates.5.validation_folds.1 | -17.4674 | -0.1747 | not_available | not_available | not_available |
| candidates.5.cost_stress | -53.6911 | -0.5369 | not_available | not_available | not_available |
| candidates.6.validation_folds.0 | 9.8323 | 0.0983 | not_available | not_available | not_available |
| candidates.6.validation_folds.1 | -13.0569 | -0.1306 | not_available | not_available | not_available |
| candidates.6.cost_stress | -40.9491 | -0.4095 | not_available | not_available | not_available |
| candidates.7.validation_folds.0 | 9.8323 | 0.0983 | not_available | not_available | not_available |
| candidates.7.validation_folds.1 | -13.0569 | -0.1306 | not_available | not_available | not_available |
| candidates.7.cost_stress | -40.9491 | -0.4095 | not_available | not_available | not_available |
| candidates.8.validation_folds.0 | -21.2681 | -0.2127 | not_available | not_available | not_available |
| candidates.8.validation_folds.1 | -54.136 | -0.5414 | not_available | not_available | not_available |
| candidates.8.cost_stress | -145.1051 | -1.4511 | not_available | not_available | not_available |
| candidates.9.validation_folds.0 | -21.2681 | -0.2127 | not_available | not_available | not_available |
| candidates.9.validation_folds.1 | -52.9862 | -0.5299 | not_available | not_available | not_available |
| candidates.9.cost_stress | -144.3612 | -1.4436 | not_available | not_available | not_available |
| candidates.10.validation_folds.0 | -2.3283 | -0.0233 | not_available | not_available | not_available |
| candidates.10.validation_folds.1 | -51.0907 | -0.5109 | not_available | not_available | not_available |
| candidates.10.cost_stress | -119.6225 | -1.1962 | not_available | not_available | not_available |
| candidates.11.validation_folds.0 | -2.3283 | -0.0233 | not_available | not_available | not_available |
| candidates.11.validation_folds.1 | -51.0907 | -0.5109 | not_available | not_available | not_available |
| candidates.11.cost_stress | -119.6225 | -1.1962 | not_available | not_available | not_available |
| candidates.12.validation_folds.0 | -45.0594 | -0.4506 | not_available | not_available | not_available |
| candidates.12.validation_folds.1 | -57.7195 | -0.5772 | not_available | not_available | not_available |
| candidates.12.cost_stress | -206.4162 | -2.0642 | not_available | not_available | not_available |
| candidates.13.validation_folds.0 | -45.0594 | -0.4506 | not_available | not_available | not_available |
| candidates.13.validation_folds.1 | -50.4712 | -0.5047 | not_available | not_available | not_available |
| candidates.13.cost_stress | -200.4539 | -2.0045 | not_available | not_available | not_available |
| candidates.14.validation_folds.0 | -21.9022 | -0.219 | not_available | not_available | not_available |
| candidates.14.validation_folds.1 | -61.9842 | -0.6198 | not_available | not_available | not_available |
| candidates.14.cost_stress | -176.6059 | -1.7661 | not_available | not_available | not_available |
| candidates.15.validation_folds.0 | -21.9022 | -0.219 | not_available | not_available | not_available |
| candidates.15.validation_folds.1 | -61.9842 | -0.6198 | not_available | not_available | not_available |
| candidates.15.cost_stress | -176.6059 | -1.7661 | not_available | not_available | not_available |
| fixed_later_comparisons.0.later_period | -1.1924 | -0.0119 | not_available | not_available | not_available |
| fixed_later_comparisons.1.later_period | -1.1924 | -0.0119 | not_available | not_available | not_available |
| fixed_later_comparisons.2.later_period | 3.7019 | 0.037 | not_available | not_available | not_available |
| fixed_later_comparisons.3.later_period | 3.7019 | 0.037 | not_available | not_available | not_available |
| fixed_later_comparisons.4.later_period | -0.7655 | -0.0077 | not_available | not_available | not_available |
| fixed_later_comparisons.5.later_period | -0.7655 | -0.0077 | not_available | not_available | not_available |
| fixed_later_comparisons.6.later_period | 2.9083 | 0.0291 | not_available | not_available | not_available |
| fixed_later_comparisons.7.later_period | 2.9083 | 0.0291 | not_available | not_available | not_available |
| fixed_later_comparisons.8.later_period | -21.8329 | -0.2183 | not_available | not_available | not_available |
| fixed_later_comparisons.9.later_period | -21.8329 | -0.2183 | not_available | not_available | not_available |
| fixed_later_comparisons.10.later_period | -19.5748 | -0.1957 | not_available | not_available | not_available |
| fixed_later_comparisons.11.later_period | -19.5748 | -0.1957 | not_available | not_available | not_available |
| fixed_later_comparisons.12.later_period | -54.7568 | -0.5476 | not_available | not_available | not_available |
| fixed_later_comparisons.13.later_period | -54.7568 | -0.5476 | not_available | not_available | not_available |
| fixed_later_comparisons.14.later_period | -52.511 | -0.5251 | not_available | not_available | not_available |
| fixed_later_comparisons.15.later_period | -52.511 | -0.5251 | not_available | not_available | not_available |


#### grok-forex-evaluation.json

Status: archived_not_recomputed; SHA-256: `5d74c12cbe7a2a1f25810437fc346eaffdc57246bab7a536603451f0dea133c8`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 10} training | 23 | 9 | 14 | -20.998 | -0.21 | 0.249 | 0.232 | [22.16, 59.21] |
| 2 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 10} training | 23 | 9 | 14 | -18.0475 | -0.1805 | 0.278 | 0.2046 | [22.16, 59.21] |
| 3 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 20} training | 45 | 20 | 25 | -34.29 | -0.3429 | 0.304 | 0.3828 | [30.94, 58.82] |
| 4 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 20} training | 45 | 20 | 25 | -31.3399 | -0.3134 | 0.323 | 0.3555 | [30.94, 58.82] |
| 5 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.0025, "threshold": 30} training | 56 | 24 | 32 | -23.7001 | -0.237 | 0.566 | 0.4271 | [30.77, 55.86] |
| 6 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.005, "threshold": 30} training | 56 | 24 | 32 | -24.9143 | -0.2491 | 0.531 | 0.4117 | [30.77, 55.86] |
| baseline | 28 | 11 | 17 | 28.0983 | 0.281 | 1.645 | 0.1927 | [23.57, 57.59] |
| fixed_later | 41 | 16 | 25 | -38.8869 | -0.3889 | 0.223 | 0.4454 | [25.66, 54.27] |
| fixed_cost_stress | 41 | 4 | 37 | -67.4262 | -0.6743 | 0.073 | 0.6825 | [3.86, 22.55] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation | -20.998 | -0.21 | not_available | not_available | not_available |
| candidates.1.validation | -18.0475 | -0.1805 | not_available | not_available | not_available |
| candidates.2.validation | -34.29 | -0.3429 | not_available | not_available | not_available |
| candidates.3.validation | -31.3399 | -0.3134 | not_available | not_available | not_available |
| candidates.4.validation | -23.7001 | -0.237 | not_available | not_available | not_available |
| candidates.5.validation | -24.9143 | -0.2491 | not_available | not_available | not_available |
| fixed_later | -38.8869 | -0.3889 | -66.9852 | -0.6699 | descriptive_same_archive_phase |
| fixed_cost_stress | -67.4262 | -0.6743 | not_available | not_available | not_available |
| baseline | 28.0983 | 0.281 | 0.0 | 0.0 | descriptive_same_archive_phase |


#### backtrader-current-reference.json

Status: archived_not_recomputed; SHA-256: `27db6c92dbc3879c13ae49f959d3441016371126ab72653a61d26198063f1f55`.
Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| <root> | None | 0.295 | not_available | not_available | not_available |


#### ml-evaluation.json

Status: archived_not_recomputed; SHA-256: `1b4da955517377096df6bf6527b4161e070fdb8918460fee26db22bd36bab4a4`.


## aapl-daily

Market/symbol: stock/AAPL. Data: **available**; validation: **not_validated**.

Input: `AAPL_1d.csv`; SHA-256: `11152ef145a7ae16467b537f55022eba139213a515f6cc0991719e2ecdc4c00e`.

Dates: 2015-02-17T00:00:00+00:00 to 2017-02-16T00:00:00+00:00; 506 bars. Timestamps are bar opens.

Gap/completeness audit: `{"calendar_status": "no_issues_detected_by_limited_calendar", "completeness": "passed", "gap_audit": {"calendar": "us_stock_daily_recurring_holidays", "calendar_limitation": "Weekends and recurring US stock holidays only; exceptional exchange closures and corporate actions are not certified", "expected_closures": 225, "interval_seconds": 86400, "missing_count": 0, "missing_timestamps_sample": [], "unexpected_closed_session_count": 0, "unexpected_closed_session_timestamps_sample": []}, "gap_handling": "No filling/interpolation; descriptive replay retains supplied observations", "structure": "passed"}`.

Cost assumptions: `{"account_currency": "USD", "config": {"capital": 10000, "commission_fraction": 0, "daily_loss_fraction": 0.02, "drawdown_fraction": 0.1, "max_notional_fraction": 0.2, "max_quote_age_seconds": 90, "max_spread_fraction": 0.005, "reward_risk": 2, "risk_fraction": 0.005, "slippage_fraction": 0.0005, "stop_fraction": 0.02}, "final_position": "liquidated_at_last_close", "intrabar": "stop_first_if_stop_and_target_both_touch", "leverage": 1, "signal_fill": "previous_closed_bars_to_next_open", "spread_absolute": null, "spread_fraction": 0.0005, "unmodeled": ["swaps", "funding", "dividends", "corporate_actions", "order_book_depth", "partial_fills", "live_latency"]}`.

Stress assumptions: `{"account_currency": "USD", "config": {"capital": 10000, "commission_fraction": 5e-05, "daily_loss_fraction": 0.02, "drawdown_fraction": 0.1, "max_notional_fraction": 0.2, "max_quote_age_seconds": 90, "max_spread_fraction": 0.005, "reward_risk": 2, "risk_fraction": 0.005, "slippage_fraction": 0.001, "stop_fraction": 0.02}, "final_position": "liquidated_at_last_close", "intrabar": "stop_first_if_stop_and_target_both_touch", "leverage": 1, "signal_fill": "previous_closed_bars_to_next_open", "spread_absolute": null, "spread_fraction": 0.001, "unmodeled": ["swaps", "funding", "dividends", "corporate_actions", "order_book_depth", "partial_fills", "live_latency"]}`.

### Reused later period

2016-07-13T00:00:00+00:00 to 2017-02-16T00:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 8 | 6 | 2 | 395.889 | 3.9589 | 5.889 | 1.3334 | [40.93, 92.85] |
| sma | 16 | 9 | 7 | 427.1836 | 4.2718 | 2.501 | 2.4157 | [33.18, 76.9] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |
| baseline cost stress | 8 | 6 | 2 | 380.3368 | 3.8034 | 5.562 | 1.357 | [40.93, 92.85] |
| sma cost stress | 16 | 8 | 8 | 342.4634 | 3.4246 | 2.01 | 2.9595 | [28.0, 72.0] |
| cash cost stress | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

### Training Folds

Each fold resets capital; earlier bars provide warm-up only.

Fold 1: 2015-09-22T00:00:00+00:00 to 2016-02-17T00:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 2 | 1 | 1 | 35.408 | 0.3541 | 1.86 | 0.4085 | [9.45, 90.55] |
| sma | 12 | 3 | 9 | -173.1082 | -1.7311 | 0.55 | 2.3894 | [8.89, 53.23] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

Fold 2: 2016-02-18T00:00:00+00:00 to 2016-07-12T00:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 5 | 2 | 3 | 28.3796 | 0.2838 | 1.226 | 1.6364 | [11.76, 76.93] |
| sma | 10 | 4 | 6 | 106.5438 | 1.0654 | 1.521 | 1.6384 | [16.82, 68.73] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

### Later Folds

Each fold resets capital; earlier bars provide warm-up only.

Fold 1: 2016-07-13T00:00:00+00:00 to 2016-09-21T00:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 1 | 1 | 0 | 134.1747 | 1.3417 | undefined | 0.6625 | [20.65, 100.0] |
| sma | 5 | 2 | 3 | 126.8792 | 1.2688 | 2.502 | 1.1761 | [11.76, 76.93] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

Fold 2: 2016-09-22T00:00:00+00:00 to 2016-12-02T00:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 2 | 0 | 2 | -57.8655 | -0.5787 | 0.0 | 1.2164 | [0.0, 65.76] |
| sma | 6 | 1 | 5 | -110.198 | -1.102 | 0.405 | 1.6228 | [3.01, 56.35] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

Fold 3: 2016-12-05T00:00:00+00:00 to 2017-02-16T00:00:00+00:00.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| baseline | 5 | 5 | 0 | 337.6414 | 3.3764 | undefined | 0.2898 | [56.55, 100.0] |
| sma | 6 | 6 | 0 | 421.3903 | 4.2139 | undefined | 0.2464 | [60.97, 100.0] |
| cash | 0 | 0 | 0 | 0 | 0 | undefined | 0 | None |

Before/after archived baseline: `{"after": {"breakeven": 0, "closed_trades": 8, "losses": 2, "max_drawdown_pct": 1.3334, "net_pnl": 395.889, "profit_factor": 5.889, "return_pct": 3.9589, "sample_win_rate_95pct_interval": [40.93, 92.85], "win_rate_pct": 75.0, "wins": 6}, "archive_file": "stock-strategy-evaluation.json", "archive_input_sha256": null, "archive_sha256": "c58d0f2a0d43a9d765054210b7a1287dd06735ffc30d8ac068fe21288bd452a2", "before": {"breakeven": 0, "closed_trades": 8, "losses": 2, "max_drawdown_pct": 1.3334, "net_pnl": 395.889, "profit_factor": 5.889, "return_pct": 3.9589, "sample_win_rate_95pct_interval": [40.93, 92.85], "win_rate_pct": 75.0, "wins": 6}, "caveat": "A metric match is not independent data verification; costs and input digests must also be reviewed", "differences": {}, "input_identity": "not_recorded_in_legacy_report", "status": "metrics_match"}`.

Baseline loss reasons: `{"stop": 2}`.

Failure/limitation reasons: previously_inspected_data_not_unseen_evidence; provenance_not_independently_certified; insufficient_closed_trade_sample; baseline_losing_or_flat_later_fold.

### Archived experiments — not recomputed

All predeclared candidates are retained in JSON; the table below includes every available candidate phase. No winners-only filter is applied.

#### stock-strategy-evaluation.json

Status: archived_not_recomputed; SHA-256: `c58d0f2a0d43a9d765054210b7a1287dd06735ffc30d8ac068fe21288bd452a2`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.02, "threshold": 5} training | 1 | 0 | 1 | -153.1388 | -1.5314 | 0.0 | 1.5942 | [0.0, 79.35] |
| 2 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.04, "threshold": 5} training | 1 | 0 | 1 | -88.6593 | -0.8866 | 0.0 | 0.9232 | [0.0, 79.35] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.02, "threshold": 10} training | 2 | 0 | 2 | -204.7118 | -2.0471 | 0.0 | 2.0471 | [0.0, 65.76] |
| 4 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.04, "threshold": 10} training | 1 | 0 | 1 | -132.362 | -1.3236 | 0.0 | 1.3236 | [0.0, 79.35] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.02, "threshold": 20} training | 2 | 0 | 2 | -204.7118 | -2.0471 | 0.0 | 2.0471 | [0.0, 65.76] |
| 6 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.04, "threshold": 20} training | 1 | 0 | 1 | -132.362 | -1.3236 | 0.0 | 1.3236 | [0.0, 79.35] |
| 7 {"family": "rsi_pullback", "reward_risk": 1.5, "stop_fraction": 0.02, "threshold": 35} training | 0 | 0 | 0 | 0 | 0.0 | undefined | 0 | None |
| 8 {"family": "rsi_pullback", "reward_risk": 1.5, "stop_fraction": 0.02, "threshold": 40} training | 0 | 0 | 0 | 0 | 0.0 | undefined | 0 | None |
| 9 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training | 2 | 0 | 2 | -57.5643 | -0.5756 | 0.0 | 1.1717 | [0.0, 65.76] |
| 10 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training | 5 | 2 | 3 | 28.3796 | 0.2838 | 1.226 | 1.6364 | [11.76, 76.93] |
| baseline | 8 | 6 | 2 | 395.889 | 3.9589 | 5.889 | 1.3334 | [40.93, 92.85] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation | -153.1388 | -1.5314 | not_available | not_available | not_available |
| candidates.1.validation | -88.6593 | -0.8866 | not_available | not_available | not_available |
| candidates.2.validation | -204.7118 | -2.0471 | not_available | not_available | not_available |
| candidates.3.validation | -132.362 | -1.3236 | not_available | not_available | not_available |
| candidates.4.validation | -204.7118 | -2.0471 | not_available | not_available | not_available |
| candidates.5.validation | -132.362 | -1.3236 | not_available | not_available | not_available |
| candidates.6.validation | 0 | 0.0 | not_available | not_available | not_available |
| candidates.7.validation | 0 | 0.0 | not_available | not_available | not_available |
| candidates.8.validation | -57.5643 | -0.5756 | not_available | not_available | not_available |
| candidates.9.validation | 28.3796 | 0.2838 | not_available | not_available | not_available |
| baseline | 395.889 | 3.9589 | 0.0 | 0.0 | descriptive_same_archive_phase |
| baseline_cost_stress | 380.3368 | 3.8034 | 0.0 | 0.0 | descriptive_same_archive_phase |



## btc-hourly

Market/symbol: crypto/BTC_USDT. Data: **not_available**; validation: **not_validated**.

Input: `BTCUSDT_1h.csv`; SHA-256: `not_available`.

Failure/limitation reasons: source_csv_not_available_no_replay_performed.

### Archived experiments — not recomputed

All predeclared candidates are retained in JSON; the table below includes every available candidate phase. No winners-only filter is applied.

#### crypto-strategy-evaluation.json

Status: archived_not_recomputed; SHA-256: `1158d9616450e2a0c57ce6ffc5c3f58b0d46a513cd8671d3a2dfaeb81ed843e2`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.01, "threshold": 5} training | 18 | 4 | 14 | -177.3161 | -1.7732 | 0.066 | 1.8975 | [9.0, 45.22] |
| 2 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.02, "threshold": 5} training | 16 | 3 | 13 | -165.8231 | -1.6582 | 0.055 | 1.7827 | [6.59, 43.01] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.01, "threshold": 10} training | 36 | 11 | 25 | -192.999 | -1.93 | 0.283 | 2.2012 | [18.0, 46.86] |
| 4 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.02, "threshold": 10} training | 33 | 10 | 23 | -157.3156 | -1.5732 | 0.325 | 1.849 | [17.38, 47.34] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.01, "threshold": 20} training | 68 | 22 | 46 | -292.8271 | -2.9283 | 0.372 | 3.1384 | [22.44, 44.16] |
| 6 {"family": "rsi2_reversion", "reward_risk": 1.5, "stop_fraction": 0.02, "threshold": 20} training | 61 | 19 | 42 | -227.3201 | -2.2732 | 0.423 | 2.4848 | [20.94, 43.59] |
| 7 {"family": "rsi_pullback", "reward_risk": 1.5, "stop_fraction": 0.01, "threshold": 35} training | 1 | 1 | 0 | 24.9556 | 0.2496 | undefined | 0.04 | [20.65, 100.0] |
| 8 {"family": "rsi_pullback", "reward_risk": 1.5, "stop_fraction": 0.01, "threshold": 40} training | 7 | 2 | 5 | -36.6946 | -0.3669 | 0.575 | 0.5997 | [8.22, 64.11] |
| 9 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training | 29 | 5 | 24 | -331.081 | -3.3108 | 0.341 | 3.8391 | [7.6, 34.55] |
| 10 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training | 70 | 18 | 52 | -579.3666 | -5.7937 | 0.486 | 6.8118 | [16.93, 37.03] |
| baseline | 55 | 15 | 40 | -122.0437 | -1.2204 | 0.843 | 3.1621 | [17.28, 40.23] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation | -177.3161 | -1.7732 | not_available | not_available | not_available |
| candidates.1.validation | -165.8231 | -1.6582 | not_available | not_available | not_available |
| candidates.2.validation | -192.999 | -1.93 | not_available | not_available | not_available |
| candidates.3.validation | -157.3156 | -1.5732 | not_available | not_available | not_available |
| candidates.4.validation | -292.8271 | -2.9283 | not_available | not_available | not_available |
| candidates.5.validation | -227.3201 | -2.2732 | not_available | not_available | not_available |
| candidates.6.validation | 24.9556 | 0.2496 | not_available | not_available | not_available |
| candidates.7.validation | -36.6946 | -0.3669 | not_available | not_available | not_available |
| candidates.8.validation | -331.081 | -3.3108 | not_available | not_available | not_available |
| candidates.9.validation | -579.3666 | -5.7937 | not_available | not_available | not_available |
| baseline | -122.0437 | -1.2204 | 0.0 | 0.0 | descriptive_same_archive_phase |
| baseline_cost_stress | -270.6559 | -2.7066 | 0.0 | 0.0 | descriptive_same_archive_phase |


#### grok-btc-evaluation.json

Status: archived_not_recomputed; SHA-256: `a8e9aef7ba5abc053158bb3c3ee82edf4f4a570089cf96c318f989f73e4f78ed`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training | 25 | 6 | 19 | -194.5998 | -1.946 | 0.094 | 1.946 | [11.5, 43.43] |
| 2 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training | 24 | 5 | 19 | -179.6121 | -1.7961 | 0.095 | 1.7961 | [9.24, 40.47] |
| 3 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} training | 51 | 13 | 38 | -374.159 | -3.7416 | 0.113 | 3.7735 | [15.55, 38.87] |
| 4 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} training | 49 | 12 | 37 | -354.1775 | -3.5418 | 0.115 | 3.5737 | [14.6, 38.09] |
| 5 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 30} training | 75 | 15 | 60 | -551.2722 | -5.5127 | 0.083 | 5.544 | [12.51, 30.41] |
| 6 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 30} training | 70 | 14 | 56 | -483.2463 | -4.8325 | 0.091 | 4.8638 | [12.3, 30.82] |
| baseline | 55 | 15 | 40 | -122.0437 | -1.2204 | 0.843 | 3.1621 | [17.28, 40.23] |
| fixed_later | 60 | 9 | 51 | -430.3654 | -4.3037 | 0.106 | 4.3037 | [8.1, 26.11] |
| fixed_cost_stress | 60 | 5 | 55 | -608.2229 | -6.0822 | 0.049 | 6.0822 | [3.61, 18.07] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation | -194.5998 | -1.946 | not_available | not_available | not_available |
| candidates.1.validation | -179.6121 | -1.7961 | not_available | not_available | not_available |
| candidates.2.validation | -374.159 | -3.7416 | not_available | not_available | not_available |
| candidates.3.validation | -354.1775 | -3.5418 | not_available | not_available | not_available |
| candidates.4.validation | -551.2722 | -5.5127 | not_available | not_available | not_available |
| candidates.5.validation | -483.2463 | -4.8325 | not_available | not_available | not_available |
| fixed_later | -430.3654 | -4.3037 | -308.3217 | -3.0833 | descriptive_same_archive_phase |
| fixed_cost_stress | -608.2229 | -6.0822 | not_available | not_available | not_available |
| baseline | -122.0437 | -1.2204 | 0.0 | 0.0 | descriptive_same_archive_phase |



## btc-extended-hourly

Market/symbol: crypto/BTC_USDT. Data: **not_available**; validation: **not_validated**.

Input: `BTCUSDT_2025_2026.csv`; SHA-256: `not_available`.

Failure/limitation reasons: source_csv_not_available_no_replay_performed.

### Archived experiments — not recomputed

All predeclared candidates are retained in JSON; the table below includes every available candidate phase. No winners-only filter is applied.

#### lab-btc-evaluation.json

Status: archived_not_recomputed; SHA-256: `ac9d91340d616dbe9b5ecd09a0d17a3b7bfac4df32b03aff41d8dc72b64794be`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 1 | 3 | 1 | 2 | -6.0712 | -0.0607 | 0.462 | 0.3536 | [6.15, 79.23] |
| 1 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 2 | 1 | 0 | 1 | -44.9372 | -0.4494 | 0.0 | 0.4494 | [0.0, 79.35] |
| 1 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training stress | 4 | 1 | 3 | -61.7003 | -0.617 | 0.031 | 0.6591 | [4.56, 69.94] |
| 2 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training fold 1 | 8 | 5 | 3 | -34.5102 | -0.3451 | 0.387 | 0.5123 | [30.57, 86.32] |
| 2 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training fold 2 | 6 | 2 | 4 | -89.9079 | -0.8991 | 0.367 | 0.943 | [9.68, 70.0] |
| 2 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training stress | 14 | 4 | 10 | -160.393 | -1.6039 | 0.253 | 1.6456 | [11.72, 54.65] |
| 3 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 1 | 21 | 10 | 11 | -222.3487 | -2.2235 | 0.413 | 2.7931 | [28.34, 67.63] |
| 3 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 2 | 20 | 10 | 10 | -237.5385 | -2.3754 | 0.466 | 2.7035 | [29.93, 70.07] |
| 3 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training stress | 41 | 18 | 23 | -545.1741 | -5.4517 | 0.353 | 5.8128 | [29.89, 58.96] |
| 4 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training fold 1 | 38 | 19 | 19 | -392.9807 | -3.9298 | 0.365 | 4.451 | [34.85, 65.15] |
| 4 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training fold 2 | 39 | 18 | 21 | -386.1559 | -3.8616 | 0.506 | 4.2098 | [31.57, 61.43] |
| 4 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training stress | 77 | 34 | 43 | -927.7366 | -9.2774 | 0.348 | 9.5904 | [33.61, 55.26] |
| 5 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 40} training fold 1 | 44 | 11 | 33 | -242.7377 | -2.4274 | 0.469 | 3.0067 | [14.57, 39.44] |
| 5 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 40} training fold 2 | 36 | 9 | 27 | -267.5148 | -2.6751 | 0.497 | 2.7733 | [13.75, 41.07] |
| 5 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 40} training stress | 80 | 17 | 63 | -759.4 | -7.594 | 0.343 | 8.112 | [13.71, 31.42] |
| 6 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training fold 1 | 44 | 11 | 33 | -260.6098 | -2.6061 | 0.504 | 3.5682 | [14.57, 39.44] |
| 6 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training fold 2 | 36 | 9 | 27 | -207.4289 | -2.0743 | 0.641 | 3.6336 | [13.75, 41.07] |
| 6 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training stress | 80 | 18 | 62 | -682.5997 | -6.826 | 0.454 | 8.9561 | [14.73, 32.79] |
| 7 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 74 | 21 | 53 | -569.8388 | -5.6984 | 0.535 | 6.0668 | [19.37, 39.52] |
| 7 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 81 | 22 | 59 | -695.6109 | -6.9561 | 0.607 | 8.2372 | [18.67, 37.72] |
| 7 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training stress | 79 | 19 | 60 | -976.4953 | -9.765 | 0.377 | 10.0449 | [15.97, 34.54] |
| 8 {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training fold 1 | 12 | 2 | 10 | -96.3617 | -0.9636 | 0.413 | 1.2845 | [4.7, 44.8] |
| 8 {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training fold 2 | 18 | 3 | 15 | -135.0628 | -1.3506 | 0.535 | 2.3669 | [5.84, 39.22] |
| 8 {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training stress | 30 | 5 | 25 | -326.0448 | -3.2604 | 0.388 | 4.1858 | [7.34, 33.56] |
| 9 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 59 | 11 | 48 | -531.1085 | -5.3111 | 0.097 | 5.4347 | [10.74, 30.38] |
| 9 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 62 | 22 | 40 | -444.7089 | -4.4471 | 0.267 | 4.5412 | [24.74, 47.92] |
| 9 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training stress | 85 | 12 | 73 | -1000.2095 | -10.0021 | 0.048 | 10.0605 | [8.26, 23.07] |
| 10 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 42 | 10 | 32 | -416.1912 | -4.1619 | 0.428 | 4.8934 | [13.48, 38.53] |
| 10 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 40 | 10 | 30 | -360.3459 | -3.6035 | 0.612 | 5.3078 | [14.19, 40.19] |
| 10 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training stress | 59 | 11 | 48 | -971.6868 | -9.7169 | 0.273 | 10.0481 | [10.74, 30.38] |
| {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} reused later | 2 | 0 | 2 | -6.1206 | -0.0612 | 0.0 | 0.1994 | [0.0, 65.76] |
| {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} reused later | 14 | 6 | 8 | -17.1705 | -0.1717 | 0.844 | 0.7422 | [21.38, 67.41] |
| {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} reused later | 34 | 14 | 20 | -302.0856 | -3.0209 | 0.429 | 4.0693 | [26.37, 57.78] |
| {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} reused later | 55 | 24 | 31 | -543.6689 | -5.4367 | 0.381 | 6.0626 | [31.37, 56.73] |
| {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 40} reused later | 74 | 15 | 59 | -651.2787 | -6.5128 | 0.318 | 6.7953 | [12.69, 30.79] |
| {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} reused later | 74 | 15 | 59 | -435.9564 | -4.3596 | 0.536 | 5.7849 | [12.69, 30.79] |
| {"family": "trend", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} reused later | 113 | 36 | 77 | -456.4059 | -4.5641 | 0.739 | 6.2539 | [23.99, 40.92] |
| {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} reused later | 23 | 5 | 18 | -85.9744 | -0.8597 | 0.742 | 1.7315 | [9.66, 41.9] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} reused later | 95 | 28 | 67 | -410.3973 | -4.104 | 0.276 | 4.1434 | [21.25, 39.3] |
| {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} reused later | 69 | 24 | 45 | -181.5666 | -1.8157 | 0.85 | 4.4666 | [24.62, 46.55] |
| baseline | 113 | 36 | 77 | -456.4059 | -4.5641 | 0.739 | 6.2539 | [23.99, 40.92] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation_folds.0 | -6.0712 | -0.0607 | not_available | not_available | not_available |
| candidates.0.validation_folds.1 | -44.9372 | -0.4494 | not_available | not_available | not_available |
| candidates.0.cost_stress | -61.7003 | -0.617 | not_available | not_available | not_available |
| candidates.1.validation_folds.0 | -34.5102 | -0.3451 | not_available | not_available | not_available |
| candidates.1.validation_folds.1 | -89.9079 | -0.8991 | not_available | not_available | not_available |
| candidates.1.cost_stress | -160.393 | -1.6039 | not_available | not_available | not_available |
| candidates.2.validation_folds.0 | -222.3487 | -2.2235 | not_available | not_available | not_available |
| candidates.2.validation_folds.1 | -237.5385 | -2.3754 | not_available | not_available | not_available |
| candidates.2.cost_stress | -545.1741 | -5.4517 | not_available | not_available | not_available |
| candidates.3.validation_folds.0 | -392.9807 | -3.9298 | not_available | not_available | not_available |
| candidates.3.validation_folds.1 | -386.1559 | -3.8616 | not_available | not_available | not_available |
| candidates.3.cost_stress | -927.7366 | -9.2774 | not_available | not_available | not_available |
| candidates.4.validation_folds.0 | -242.7377 | -2.4274 | not_available | not_available | not_available |
| candidates.4.validation_folds.1 | -267.5148 | -2.6751 | not_available | not_available | not_available |
| candidates.4.cost_stress | -759.4 | -7.594 | not_available | not_available | not_available |
| candidates.5.validation_folds.0 | -260.6098 | -2.6061 | not_available | not_available | not_available |
| candidates.5.validation_folds.1 | -207.4289 | -2.0743 | not_available | not_available | not_available |
| candidates.5.cost_stress | -682.5997 | -6.826 | not_available | not_available | not_available |
| candidates.6.validation_folds.0 | -569.8388 | -5.6984 | not_available | not_available | not_available |
| candidates.6.validation_folds.1 | -695.6109 | -6.9561 | not_available | not_available | not_available |
| candidates.6.cost_stress | -976.4953 | -9.765 | not_available | not_available | not_available |
| candidates.7.validation_folds.0 | -96.3617 | -0.9636 | not_available | not_available | not_available |
| candidates.7.validation_folds.1 | -135.0628 | -1.3506 | not_available | not_available | not_available |
| candidates.7.cost_stress | -326.0448 | -3.2604 | not_available | not_available | not_available |
| candidates.8.validation_folds.0 | -531.1085 | -5.3111 | not_available | not_available | not_available |
| candidates.8.validation_folds.1 | -444.7089 | -4.4471 | not_available | not_available | not_available |
| candidates.8.cost_stress | -1000.2095 | -10.0021 | not_available | not_available | not_available |
| candidates.9.validation_folds.0 | -416.1912 | -4.1619 | not_available | not_available | not_available |
| candidates.9.validation_folds.1 | -360.3459 | -3.6035 | not_available | not_available | not_available |
| candidates.9.cost_stress | -971.6868 | -9.7169 | not_available | not_available | not_available |
| baseline | -456.4059 | -4.5641 | 0.0 | 0.0 | descriptive_same_archive_phase |
| fixed_later_comparisons.0.later_period | -6.1206 | -0.0612 | 450.2853 | 4.5029 | descriptive_same_archive_phase |
| fixed_later_comparisons.1.later_period | -17.1705 | -0.1717 | 439.2354 | 4.3924 | descriptive_same_archive_phase |
| fixed_later_comparisons.2.later_period | -302.0856 | -3.0209 | 154.3203 | 1.5432 | descriptive_same_archive_phase |
| fixed_later_comparisons.3.later_period | -543.6689 | -5.4367 | -87.263 | -0.8726 | descriptive_same_archive_phase |
| fixed_later_comparisons.4.later_period | -651.2787 | -6.5128 | -194.8728 | -1.9487 | descriptive_same_archive_phase |
| fixed_later_comparisons.5.later_period | -435.9564 | -4.3596 | 20.4495 | 0.2045 | descriptive_same_archive_phase |
| fixed_later_comparisons.6.later_period | -456.4059 | -4.5641 | 0.0 | 0.0 | descriptive_same_archive_phase |
| fixed_later_comparisons.7.later_period | -85.9744 | -0.8597 | 370.4315 | 3.7044 | descriptive_same_archive_phase |
| fixed_later_comparisons.8.later_period | -410.3973 | -4.104 | 46.0086 | 0.4601 | descriptive_same_archive_phase |
| fixed_later_comparisons.9.later_period | -181.5666 | -1.8157 | 274.8393 | 2.7484 | descriptive_same_archive_phase |


#### winrate-btc-evaluation.json

Status: archived_not_recomputed; SHA-256: `0fc31459d668982a6348d37855af9aeb7a0b0c52016759b784b7f25dec0ba473`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 5} training fold 1 | 33 | 5 | 28 | -254.5662 | -2.5457 | 0.058 | 2.6838 | [6.65, 30.92] |
| 1 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 5} training fold 2 | 33 | 15 | 18 | -167.9372 | -1.6794 | 0.403 | 2.106 | [29.84, 62.01] |
| 1 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 5} training stress | 68 | 14 | 54 | -604.4635 | -6.0446 | 0.119 | 6.1324 | [12.68, 31.64] |
| 2 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 5} training fold 1 | 33 | 5 | 28 | -254.5662 | -2.5457 | 0.058 | 2.6838 | [6.65, 30.92] |
| 2 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 5} training fold 2 | 33 | 15 | 18 | -167.2388 | -1.6724 | 0.406 | 2.1393 | [29.84, 62.01] |
| 2 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 5} training stress | 68 | 14 | 54 | -609.4631 | -6.0946 | 0.112 | 6.1685 | [12.68, 31.64] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 5} training fold 1 | 31 | 4 | 27 | -247.0742 | -2.4707 | 0.045 | 2.609 | [5.13, 28.85] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 5} training fold 2 | 31 | 13 | 18 | -180.8697 | -1.8087 | 0.348 | 2.082 | [26.42, 59.23] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 5} training stress | 63 | 11 | 52 | -628.577 | -6.2858 | 0.101 | 6.3466 | [10.04, 28.62] |
| 4 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 5} training fold 1 | 31 | 4 | 27 | -247.0742 | -2.4707 | 0.045 | 2.609 | [5.13, 28.85] |
| 4 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 5} training fold 2 | 31 | 13 | 18 | -180.8697 | -1.8087 | 0.348 | 2.082 | [26.42, 59.23] |
| 4 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 5} training stress | 63 | 11 | 52 | -628.577 | -6.2858 | 0.101 | 6.3466 | [10.04, 28.62] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 10} training fold 1 | 64 | 11 | 53 | -557.4407 | -5.5744 | 0.07 | 5.6977 | [9.88, 28.21] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 10} training fold 2 | 69 | 24 | 45 | -493.8381 | -4.9384 | 0.254 | 5.032 | [24.62, 46.55] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 10} training stress | 94 | 13 | 81 | -1005.0749 | -10.0507 | 0.038 | 10.1092 | [8.26, 22.24] |
| 6 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training fold 1 | 64 | 11 | 53 | -557.4407 | -5.5744 | 0.07 | 5.6977 | [9.88, 28.21] |
| 6 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training fold 2 | 69 | 24 | 45 | -495.7933 | -4.9579 | 0.251 | 5.0515 | [24.62, 46.55] |
| 6 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training stress | 93 | 13 | 80 | -996.8773 | -9.9688 | 0.035 | 10.0272 | [8.35, 22.46] |
| 7 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 59 | 11 | 48 | -531.1085 | -5.3111 | 0.097 | 5.4347 | [10.74, 30.38] |
| 7 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 62 | 22 | 40 | -446.7978 | -4.468 | 0.263 | 4.5621 | [24.74, 47.92] |
| 7 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 10} training stress | 85 | 12 | 73 | -1000.2095 | -10.0021 | 0.048 | 10.0605 | [8.26, 23.07] |
| 8 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 59 | 11 | 48 | -531.1085 | -5.3111 | 0.097 | 5.4347 | [10.74, 30.38] |
| 8 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 62 | 22 | 40 | -444.7089 | -4.4471 | 0.267 | 4.5412 | [24.74, 47.92] |
| 8 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training stress | 85 | 12 | 73 | -1000.2095 | -10.0021 | 0.048 | 10.0605 | [8.26, 23.07] |
| 9 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 20} training fold 1 | 106 | 26 | 80 | -777.6513 | -7.7765 | 0.097 | 7.8558 | [17.32, 33.51] |
| 9 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 20} training fold 2 | 138 | 51 | 87 | -804.9651 | -8.0497 | 0.309 | 8.1084 | [29.36, 45.26] |
| 9 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 20} training stress | 94 | 9 | 85 | -1001.2494 | -10.0125 | 0.02 | 10.0709 | [5.12, 17.2] |
| 10 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} training fold 1 | 106 | 26 | 80 | -777.6513 | -7.7765 | 0.097 | 7.8558 | [17.32, 33.51] |
| 10 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} training fold 2 | 138 | 51 | 87 | -807.8288 | -8.0783 | 0.306 | 8.0783 | [29.36, 45.26] |
| 10 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} training stress | 94 | 9 | 85 | -1001.2494 | -10.0125 | 0.02 | 10.0709 | [5.12, 17.2] |
| 11 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 20} training fold 1 | 96 | 24 | 72 | -768.4166 | -7.6842 | 0.108 | 7.7635 | [17.41, 34.51] |
| 11 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 20} training fold 2 | 118 | 44 | 74 | -654.0649 | -6.5406 | 0.334 | 6.8121 | [29.09, 46.28] |
| 11 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 20} training stress | 89 | 8 | 81 | -1003.2293 | -10.0323 | 0.032 | 10.0907 | [4.63, 16.75] |
| 12 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} training fold 1 | 96 | 24 | 72 | -768.4166 | -7.6842 | 0.108 | 7.7635 | [17.41, 34.51] |
| 12 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} training fold 2 | 118 | 44 | 74 | -663.8682 | -6.6387 | 0.324 | 6.8404 | [29.09, 46.28] |
| 12 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} training stress | 89 | 8 | 81 | -1003.2293 | -10.0323 | 0.032 | 10.0907 | [4.63, 16.75] |
| 13 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 35} training fold 1 | 141 | 23 | 118 | -1004.5302 | -10.0453 | 0.072 | 10.0453 | [11.12, 23.29] |
| 13 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 35} training fold 2 | 146 | 37 | 109 | -1013.8664 | -10.1387 | 0.211 | 10.1829 | [18.98, 32.97] |
| 13 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 35} training stress | 92 | 5 | 87 | -1007.1564 | -10.0716 | 0.013 | 10.0716 | [2.34, 12.1] |
| 14 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 35} training fold 1 | 141 | 23 | 118 | -1004.9783 | -10.0498 | 0.072 | 10.0498 | [11.12, 23.29] |
| 14 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 35} training fold 2 | 146 | 37 | 109 | -1017.2282 | -10.1723 | 0.209 | 10.1723 | [18.98, 32.97] |
| 14 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 35} training stress | 92 | 5 | 87 | -1007.1564 | -10.0716 | 0.013 | 10.0716 | [2.34, 12.1] |
| 15 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 35} training fold 1 | 135 | 22 | 113 | -1006.9418 | -10.0694 | 0.072 | 10.0694 | [11.02, 23.44] |
| 15 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 35} training fold 2 | 146 | 39 | 107 | -984.247 | -9.8425 | 0.207 | 10.0372 | [20.2, 34.42] |
| 15 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 35} training stress | 95 | 4 | 91 | -1004.3324 | -10.0433 | 0.015 | 10.0433 | [1.65, 10.33] |
| 16 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 1 | 135 | 22 | 113 | -1006.9418 | -10.0694 | 0.072 | 10.0694 | [11.02, 23.44] |
| 16 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 2 | 147 | 39 | 108 | -987.2116 | -9.8721 | 0.213 | 10.0668 | [20.06, 34.2] |
| 16 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training stress | 95 | 4 | 91 | -1004.3324 | -10.0433 | 0.015 | 10.0433 | [1.65, 10.33] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 5} reused later | 52 | 16 | 36 | -294.2136 | -2.9421 | 0.25 | 3.126 | [19.91, 44.27] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 5} reused later | 52 | 15 | 37 | -312.9889 | -3.1299 | 0.205 | 3.2998 | [18.33, 42.27] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 5} reused later | 47 | 13 | 34 | -249.6803 | -2.4968 | 0.195 | 2.6936 | [16.94, 41.76] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 5} reused later | 47 | 13 | 34 | -249.6803 | -2.4968 | 0.195 | 2.6936 | [16.94, 41.76] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 10} reused later | 102 | 32 | 70 | -488.6796 | -4.8868 | 0.257 | 4.9172 | [23.18, 40.91] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} reused later | 102 | 31 | 71 | -482.2483 | -4.8225 | 0.269 | 4.8529 | [22.31, 39.9] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 10} reused later | 95 | 28 | 67 | -410.3973 | -4.104 | 0.276 | 4.1434 | [21.25, 39.3] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} reused later | 95 | 28 | 67 | -410.3973 | -4.104 | 0.276 | 4.1434 | [21.25, 39.3] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 20} reused later | 189 | 52 | 137 | -1007.2364 | -10.0724 | 0.234 | 10.0724 | [21.64, 34.28] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} reused later | 190 | 51 | 139 | -1005.6636 | -10.0566 | 0.251 | 10.0566 | [21.05, 33.56] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 20} reused later | 182 | 48 | 134 | -959.6044 | -9.596 | 0.248 | 9.6528 | [20.51, 33.22] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} reused later | 182 | 48 | 134 | -963.3639 | -9.6336 | 0.245 | 9.6904 | [20.51, 33.22] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 35} reused later | 164 | 45 | 119 | -986.9137 | -9.8691 | 0.201 | 10.0281 | [21.19, 34.73] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 35} reused later | 173 | 46 | 127 | -988.9417 | -9.8894 | 0.228 | 10.0978 | [20.57, 33.63] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 35} reused later | 159 | 40 | 119 | -982.3919 | -9.8239 | 0.213 | 10.0324 | [19.05, 32.43] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} reused later | 159 | 40 | 119 | -982.3919 | -9.8239 | 0.213 | 10.0324 | [19.05, 32.43] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation_folds.0 | -254.5662 | -2.5457 | not_available | not_available | not_available |
| candidates.0.validation_folds.1 | -167.9372 | -1.6794 | not_available | not_available | not_available |
| candidates.0.cost_stress | -604.4635 | -6.0446 | not_available | not_available | not_available |
| candidates.1.validation_folds.0 | -254.5662 | -2.5457 | not_available | not_available | not_available |
| candidates.1.validation_folds.1 | -167.2388 | -1.6724 | not_available | not_available | not_available |
| candidates.1.cost_stress | -609.4631 | -6.0946 | not_available | not_available | not_available |
| candidates.2.validation_folds.0 | -247.0742 | -2.4707 | not_available | not_available | not_available |
| candidates.2.validation_folds.1 | -180.8697 | -1.8087 | not_available | not_available | not_available |
| candidates.2.cost_stress | -628.577 | -6.2858 | not_available | not_available | not_available |
| candidates.3.validation_folds.0 | -247.0742 | -2.4707 | not_available | not_available | not_available |
| candidates.3.validation_folds.1 | -180.8697 | -1.8087 | not_available | not_available | not_available |
| candidates.3.cost_stress | -628.577 | -6.2858 | not_available | not_available | not_available |
| candidates.4.validation_folds.0 | -557.4407 | -5.5744 | not_available | not_available | not_available |
| candidates.4.validation_folds.1 | -493.8381 | -4.9384 | not_available | not_available | not_available |
| candidates.4.cost_stress | -1005.0749 | -10.0507 | not_available | not_available | not_available |
| candidates.5.validation_folds.0 | -557.4407 | -5.5744 | not_available | not_available | not_available |
| candidates.5.validation_folds.1 | -495.7933 | -4.9579 | not_available | not_available | not_available |
| candidates.5.cost_stress | -996.8773 | -9.9688 | not_available | not_available | not_available |
| candidates.6.validation_folds.0 | -531.1085 | -5.3111 | not_available | not_available | not_available |
| candidates.6.validation_folds.1 | -446.7978 | -4.468 | not_available | not_available | not_available |
| candidates.6.cost_stress | -1000.2095 | -10.0021 | not_available | not_available | not_available |
| candidates.7.validation_folds.0 | -531.1085 | -5.3111 | not_available | not_available | not_available |
| candidates.7.validation_folds.1 | -444.7089 | -4.4471 | not_available | not_available | not_available |
| candidates.7.cost_stress | -1000.2095 | -10.0021 | not_available | not_available | not_available |
| candidates.8.validation_folds.0 | -777.6513 | -7.7765 | not_available | not_available | not_available |
| candidates.8.validation_folds.1 | -804.9651 | -8.0497 | not_available | not_available | not_available |
| candidates.8.cost_stress | -1001.2494 | -10.0125 | not_available | not_available | not_available |
| candidates.9.validation_folds.0 | -777.6513 | -7.7765 | not_available | not_available | not_available |
| candidates.9.validation_folds.1 | -807.8288 | -8.0783 | not_available | not_available | not_available |
| candidates.9.cost_stress | -1001.2494 | -10.0125 | not_available | not_available | not_available |
| candidates.10.validation_folds.0 | -768.4166 | -7.6842 | not_available | not_available | not_available |
| candidates.10.validation_folds.1 | -654.0649 | -6.5406 | not_available | not_available | not_available |
| candidates.10.cost_stress | -1003.2293 | -10.0323 | not_available | not_available | not_available |
| candidates.11.validation_folds.0 | -768.4166 | -7.6842 | not_available | not_available | not_available |
| candidates.11.validation_folds.1 | -663.8682 | -6.6387 | not_available | not_available | not_available |
| candidates.11.cost_stress | -1003.2293 | -10.0323 | not_available | not_available | not_available |
| candidates.12.validation_folds.0 | -1004.5302 | -10.0453 | not_available | not_available | not_available |
| candidates.12.validation_folds.1 | -1013.8664 | -10.1387 | not_available | not_available | not_available |
| candidates.12.cost_stress | -1007.1564 | -10.0716 | not_available | not_available | not_available |
| candidates.13.validation_folds.0 | -1004.9783 | -10.0498 | not_available | not_available | not_available |
| candidates.13.validation_folds.1 | -1017.2282 | -10.1723 | not_available | not_available | not_available |
| candidates.13.cost_stress | -1007.1564 | -10.0716 | not_available | not_available | not_available |
| candidates.14.validation_folds.0 | -1006.9418 | -10.0694 | not_available | not_available | not_available |
| candidates.14.validation_folds.1 | -984.247 | -9.8425 | not_available | not_available | not_available |
| candidates.14.cost_stress | -1004.3324 | -10.0433 | not_available | not_available | not_available |
| candidates.15.validation_folds.0 | -1006.9418 | -10.0694 | not_available | not_available | not_available |
| candidates.15.validation_folds.1 | -987.2116 | -9.8721 | not_available | not_available | not_available |
| candidates.15.cost_stress | -1004.3324 | -10.0433 | not_available | not_available | not_available |
| fixed_later_comparisons.0.later_period | -294.2136 | -2.9421 | not_available | not_available | not_available |
| fixed_later_comparisons.1.later_period | -312.9889 | -3.1299 | not_available | not_available | not_available |
| fixed_later_comparisons.2.later_period | -249.6803 | -2.4968 | not_available | not_available | not_available |
| fixed_later_comparisons.3.later_period | -249.6803 | -2.4968 | not_available | not_available | not_available |
| fixed_later_comparisons.4.later_period | -488.6796 | -4.8868 | not_available | not_available | not_available |
| fixed_later_comparisons.5.later_period | -482.2483 | -4.8225 | not_available | not_available | not_available |
| fixed_later_comparisons.6.later_period | -410.3973 | -4.104 | not_available | not_available | not_available |
| fixed_later_comparisons.7.later_period | -410.3973 | -4.104 | not_available | not_available | not_available |
| fixed_later_comparisons.8.later_period | -1007.2364 | -10.0724 | not_available | not_available | not_available |
| fixed_later_comparisons.9.later_period | -1005.6636 | -10.0566 | not_available | not_available | not_available |
| fixed_later_comparisons.10.later_period | -959.6044 | -9.596 | not_available | not_available | not_available |
| fixed_later_comparisons.11.later_period | -963.3639 | -9.6336 | not_available | not_available | not_available |
| fixed_later_comparisons.12.later_period | -986.9137 | -9.8691 | not_available | not_available | not_available |
| fixed_later_comparisons.13.later_period | -988.9417 | -9.8894 | not_available | not_available | not_available |
| fixed_later_comparisons.14.later_period | -982.3919 | -9.8239 | not_available | not_available | not_available |
| fixed_later_comparisons.15.later_period | -982.3919 | -9.8239 | not_available | not_available | not_available |



## eth-hourly

Market/symbol: crypto/ETH_USDT. Data: **not_available**; validation: **not_validated**.

Input: `ETHUSDT_1h.csv`; SHA-256: `not_available`.

Failure/limitation reasons: source_csv_not_available_no_replay_performed.

### Archived experiments — not recomputed

All predeclared candidates are retained in JSON; the table below includes every available candidate phase. No winners-only filter is applied.

#### lab-eth-evaluation.json

Status: archived_not_recomputed; SHA-256: `fe2a2293bd84e8040f55343723e117afe48f9520c72cffda9df666a87f23abc1`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 1 | 1 | 1 | 0 | 10.1961 | 0.102 | undefined | 0.1128 | [20.65, 100.0] |
| 1 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 2 | 0 | 0 | 0 | 0 | 0.0 | undefined | 0 | None |
| 1 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training stress | 1 | 1 | 0 | 6.9795 | 0.0698 | undefined | 0.1337 | [20.65, 100.0] |
| 2 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training fold 1 | 5 | 2 | 3 | -111.0296 | -1.1103 | 0.174 | 1.1103 | [11.76, 76.93] |
| 2 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training fold 2 | 4 | 2 | 2 | -2.5182 | -0.0252 | 0.948 | 0.4798 | [15.0, 85.0] |
| 2 {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training stress | 9 | 3 | 6 | -187.4299 | -1.8743 | 0.204 | 1.9125 | [12.06, 64.58] |
| 3 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 1 | 4 | 2 | 2 | -25.8308 | -0.2583 | 0.45 | 0.5864 | [15.0, 85.0] |
| 3 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 2 | 8 | 4 | 4 | -66.1194 | -0.6612 | 0.63 | 2.0625 | [21.52, 78.48] |
| 3 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training stress | 12 | 6 | 6 | -119.9617 | -1.1996 | 0.487 | 2.3998 | [25.38, 74.62] |
| 4 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training fold 1 | 11 | 4 | 7 | -227.5978 | -2.276 | 0.154 | 2.5225 | [15.17, 64.62] |
| 4 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training fold 2 | 18 | 10 | 8 | -110.7539 | -1.1075 | 0.594 | 2.3846 | [33.72, 75.44] |
| 4 {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} training stress | 29 | 13 | 16 | -402.1442 | -4.0214 | 0.279 | 4.5995 | [28.41, 62.45] |
| 5 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 40} training fold 1 | 21 | 7 | 14 | -66.4775 | -0.6648 | 0.754 | 1.4782 | [17.19, 54.63] |
| 5 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 40} training fold 2 | 8 | 2 | 6 | -31.089 | -0.3109 | 0.691 | 0.7097 | [7.15, 59.07] |
| 5 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 40} training stress | 29 | 9 | 20 | -153.3976 | -1.534 | 0.626 | 2.4925 | [17.28, 49.23] |
| 6 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training fold 1 | 21 | 7 | 14 | -4.7888 | -0.0479 | 0.986 | 1.9994 | [17.19, 54.63] |
| 6 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training fold 2 | 8 | 1 | 7 | -70.0416 | -0.7004 | 0.515 | 0.842 | [2.24, 47.09] |
| 6 {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training stress | 29 | 8 | 21 | -168.2822 | -1.6828 | 0.695 | 3.2344 | [14.7, 45.72] |
| 7 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 36 | 10 | 26 | -238.8219 | -2.3882 | 0.664 | 2.4219 | [15.85, 43.99] |
| 7 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 34 | 9 | 25 | -244.8457 | -2.4485 | 0.645 | 3.4794 | [14.6, 43.12] |
| 7 {"family": "trend", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training stress | 70 | 16 | 54 | -791.9795 | -7.9198 | 0.496 | 8.7875 | [14.59, 33.95] |
| 8 {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training fold 1 | 8 | 3 | 5 | 113.9288 | 1.1393 | 2.019 | 0.6787 | [13.68, 69.43] |
| 8 {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training fold 2 | 5 | 0 | 5 | -148.6359 | -1.4864 | 0.0 | 1.4864 | [-0.0, 43.45] |
| 8 {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} training stress | 13 | 3 | 10 | -80.0268 | -0.8003 | 0.723 | 2.3643 | [8.18, 50.26] |
| 9 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 28 | 9 | 19 | -153.3633 | -1.5336 | 0.447 | 1.5375 | [17.93, 50.66] |
| 9 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 22 | 6 | 16 | -220.8294 | -2.2083 | 0.223 | 2.3651 | [13.15, 48.15] |
| 9 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training stress | 50 | 9 | 41 | -510.2334 | -5.1023 | 0.224 | 5.1977 | [9.77, 30.8] |
| 10 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 20 | 4 | 16 | -275.4989 | -2.755 | 0.468 | 3.1571 | [8.07, 41.6] |
| 10 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 18 | 4 | 14 | -272.536 | -2.7254 | 0.463 | 3.4336 | [9.0, 45.22] |
| 10 {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training stress | 38 | 8 | 30 | -617.6759 | -6.1768 | 0.425 | 7.0229 | [11.07, 36.35] |
| {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} reused later | 5 | 4 | 1 | 4.6137 | 0.0461 | 1.103 | 0.5772 | [37.55, 96.38] |
| {"family": "band_recovery", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} reused later | 12 | 7 | 5 | -61.7227 | -0.6172 | 0.586 | 1.2232 | [31.95, 80.67] |
| {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} reused later | 6 | 4 | 2 | 52.0176 | 0.5202 | 2.71 | 0.4023 | [30.0, 90.32] |
| {"family": "range_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 45} reused later | 18 | 10 | 8 | -101.9654 | -1.0197 | 0.577 | 1.3662 | [33.72, 75.44] |
| {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 40} reused later | 48 | 12 | 36 | -259.79 | -2.5979 | 0.579 | 2.7002 | [14.92, 38.78] |
| {"family": "macd_swing", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} reused later | 48 | 11 | 37 | -235.2959 | -2.353 | 0.657 | 2.8304 | [13.31, 36.54] |
| {"family": "trend", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} reused later | 63 | 20 | 43 | -45.8151 | -0.4582 | 0.958 | 3.3855 | [21.59, 44.0] |
| {"family": "rsi_pullback", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 40} reused later | 9 | 3 | 6 | -9.662 | -0.0966 | 0.938 | 1.4277 | [12.06, 64.58] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} reused later | 33 | 15 | 18 | -235.7019 | -2.357 | 0.169 | 2.4131 | [29.84, 62.01] |
| {"family": "donchian", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} reused later | 36 | 12 | 24 | -143.6274 | -1.4363 | 0.829 | 3.6734 | [20.21, 49.67] |
| baseline | 63 | 20 | 43 | -45.8151 | -0.4582 | 0.958 | 3.3855 | [21.59, 44.0] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation_folds.0 | 10.1961 | 0.102 | not_available | not_available | not_available |
| candidates.0.validation_folds.1 | 0 | 0.0 | not_available | not_available | not_available |
| candidates.0.cost_stress | 6.9795 | 0.0698 | not_available | not_available | not_available |
| candidates.1.validation_folds.0 | -111.0296 | -1.1103 | not_available | not_available | not_available |
| candidates.1.validation_folds.1 | -2.5182 | -0.0252 | not_available | not_available | not_available |
| candidates.1.cost_stress | -187.4299 | -1.8743 | not_available | not_available | not_available |
| candidates.2.validation_folds.0 | -25.8308 | -0.2583 | not_available | not_available | not_available |
| candidates.2.validation_folds.1 | -66.1194 | -0.6612 | not_available | not_available | not_available |
| candidates.2.cost_stress | -119.9617 | -1.1996 | not_available | not_available | not_available |
| candidates.3.validation_folds.0 | -227.5978 | -2.276 | not_available | not_available | not_available |
| candidates.3.validation_folds.1 | -110.7539 | -1.1075 | not_available | not_available | not_available |
| candidates.3.cost_stress | -402.1442 | -4.0214 | not_available | not_available | not_available |
| candidates.4.validation_folds.0 | -66.4775 | -0.6648 | not_available | not_available | not_available |
| candidates.4.validation_folds.1 | -31.089 | -0.3109 | not_available | not_available | not_available |
| candidates.4.cost_stress | -153.3976 | -1.534 | not_available | not_available | not_available |
| candidates.5.validation_folds.0 | -4.7888 | -0.0479 | not_available | not_available | not_available |
| candidates.5.validation_folds.1 | -70.0416 | -0.7004 | not_available | not_available | not_available |
| candidates.5.cost_stress | -168.2822 | -1.6828 | not_available | not_available | not_available |
| candidates.6.validation_folds.0 | -238.8219 | -2.3882 | not_available | not_available | not_available |
| candidates.6.validation_folds.1 | -244.8457 | -2.4485 | not_available | not_available | not_available |
| candidates.6.cost_stress | -791.9795 | -7.9198 | not_available | not_available | not_available |
| candidates.7.validation_folds.0 | 113.9288 | 1.1393 | not_available | not_available | not_available |
| candidates.7.validation_folds.1 | -148.6359 | -1.4864 | not_available | not_available | not_available |
| candidates.7.cost_stress | -80.0268 | -0.8003 | not_available | not_available | not_available |
| candidates.8.validation_folds.0 | -153.3633 | -1.5336 | not_available | not_available | not_available |
| candidates.8.validation_folds.1 | -220.8294 | -2.2083 | not_available | not_available | not_available |
| candidates.8.cost_stress | -510.2334 | -5.1023 | not_available | not_available | not_available |
| candidates.9.validation_folds.0 | -275.4989 | -2.755 | not_available | not_available | not_available |
| candidates.9.validation_folds.1 | -272.536 | -2.7254 | not_available | not_available | not_available |
| candidates.9.cost_stress | -617.6759 | -6.1768 | not_available | not_available | not_available |
| baseline | -45.8151 | -0.4582 | 0.0 | 0.0 | descriptive_same_archive_phase |
| fixed_later_comparisons.0.later_period | 4.6137 | 0.0461 | 50.4288 | 0.5043 | descriptive_same_archive_phase |
| fixed_later_comparisons.1.later_period | -61.7227 | -0.6172 | -15.9076 | -0.159 | descriptive_same_archive_phase |
| fixed_later_comparisons.2.later_period | 52.0176 | 0.5202 | 97.8327 | 0.9784 | descriptive_same_archive_phase |
| fixed_later_comparisons.3.later_period | -101.9654 | -1.0197 | -56.1503 | -0.5615 | descriptive_same_archive_phase |
| fixed_later_comparisons.4.later_period | -259.79 | -2.5979 | -213.9749 | -2.1397 | descriptive_same_archive_phase |
| fixed_later_comparisons.5.later_period | -235.2959 | -2.353 | -189.4808 | -1.8948 | descriptive_same_archive_phase |
| fixed_later_comparisons.6.later_period | -45.8151 | -0.4582 | 0.0 | 0.0 | descriptive_same_archive_phase |
| fixed_later_comparisons.7.later_period | -9.662 | -0.0966 | 36.1531 | 0.3616 | descriptive_same_archive_phase |
| fixed_later_comparisons.8.later_period | -235.7019 | -2.357 | -189.8868 | -1.8988 | descriptive_same_archive_phase |
| fixed_later_comparisons.9.later_period | -143.6274 | -1.4363 | -97.8123 | -0.9781 | descriptive_same_archive_phase |


#### winrate-eth-evaluation.json

Status: archived_not_recomputed; SHA-256: `eec1a788a5d721dd8e2c9e6c27300c913671fd7eab1ca784f8a17585d7f3f7a9`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 5} training fold 1 | 18 | 4 | 14 | -147.3276 | -1.4733 | 0.234 | 1.6429 | [9.0, 45.22] |
| 1 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 5} training fold 2 | 14 | 4 | 10 | -160.6564 | -1.6066 | 0.168 | 1.7181 | [11.72, 54.65] |
| 1 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 5} training stress | 34 | 5 | 29 | -437.2991 | -4.373 | 0.113 | 4.4821 | [6.45, 30.13] |
| 2 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 5} training fold 1 | 18 | 4 | 14 | -168.8227 | -1.6882 | 0.121 | 1.7736 | [9.0, 45.22] |
| 2 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 5} training fold 2 | 14 | 4 | 10 | -156.3692 | -1.5637 | 0.191 | 1.6752 | [11.72, 54.65] |
| 2 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 5} training stress | 34 | 5 | 29 | -449.6321 | -4.4963 | 0.087 | 4.6053 | [6.45, 30.13] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 5} training fold 1 | 14 | 2 | 12 | -147.3358 | -1.4734 | 0.017 | 1.5588 | [4.01, 39.94] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 5} training fold 2 | 12 | 4 | 8 | -104.1386 | -1.0414 | 0.234 | 1.2214 | [13.81, 60.94] |
| 3 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 5} training stress | 26 | 2 | 24 | -324.7581 | -3.2476 | 0.064 | 3.358 | [2.14, 24.14] |
| 4 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 5} training fold 1 | 14 | 2 | 12 | -147.3358 | -1.4734 | 0.017 | 1.5588 | [4.01, 39.94] |
| 4 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 5} training fold 2 | 12 | 4 | 8 | -104.1386 | -1.0414 | 0.234 | 1.2214 | [13.81, 60.94] |
| 4 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 5} training stress | 26 | 2 | 24 | -324.7581 | -3.2476 | 0.064 | 3.358 | [2.14, 24.14] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 10} training fold 1 | 36 | 10 | 26 | -306.7752 | -3.0678 | 0.246 | 3.0678 | [15.85, 43.99] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 10} training fold 2 | 26 | 7 | 19 | -285.0106 | -2.8501 | 0.166 | 2.8508 | [13.7, 46.08] |
| 5 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 10} training stress | 67 | 12 | 55 | -807.9802 | -8.0798 | 0.129 | 8.1727 | [10.55, 28.75] |
| 6 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training fold 1 | 36 | 10 | 26 | -289.2664 | -2.8927 | 0.289 | 2.8927 | [15.85, 43.99] |
| 6 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training fold 2 | 26 | 7 | 19 | -279.1916 | -2.7919 | 0.183 | 2.8269 | [13.7, 46.08] |
| 6 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training stress | 67 | 12 | 55 | -787.2347 | -7.8723 | 0.152 | 7.9654 | [10.55, 28.75] |
| 7 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 28 | 9 | 19 | -159.9191 | -1.5992 | 0.423 | 1.6031 | [17.93, 50.66] |
| 7 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 22 | 6 | 16 | -220.8294 | -2.2083 | 0.223 | 2.3651 | [13.15, 48.15] |
| 7 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 10} training stress | 50 | 9 | 41 | -514.6211 | -5.1462 | 0.217 | 5.2415 | [9.77, 30.8] |
| 8 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 1 | 28 | 9 | 19 | -153.3633 | -1.5336 | 0.447 | 1.5375 | [17.93, 50.66] |
| 8 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training fold 2 | 22 | 6 | 16 | -220.8294 | -2.2083 | 0.223 | 2.3651 | [13.15, 48.15] |
| 8 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training stress | 50 | 9 | 41 | -510.2334 | -5.1023 | 0.224 | 5.1977 | [9.77, 30.8] |
| 9 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 20} training fold 1 | 65 | 25 | 40 | -448.6676 | -4.4867 | 0.3 | 4.4867 | [27.59, 50.62] |
| 9 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 20} training fold 2 | 42 | 12 | 30 | -362.0295 | -3.6203 | 0.215 | 3.6203 | [17.17, 43.57] |
| 9 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 20} training stress | 101 | 23 | 78 | -1009.8864 | -10.0989 | 0.163 | 10.0989 | [15.68, 31.86] |
| 10 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} training fold 1 | 65 | 25 | 40 | -419.8057 | -4.1981 | 0.345 | 4.3019 | [27.59, 50.62] |
| 10 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} training fold 2 | 42 | 12 | 30 | -356.3469 | -3.5635 | 0.228 | 3.5635 | [17.17, 43.57] |
| 10 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} training stress | 103 | 23 | 80 | -1005.9426 | -10.0594 | 0.181 | 10.0594 | [15.37, 31.28] |
| 11 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 20} training fold 1 | 52 | 24 | 28 | -287.3718 | -2.8737 | 0.425 | 2.8775 | [33.34, 59.5] |
| 11 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 20} training fold 2 | 35 | 11 | 24 | -301.1384 | -3.0114 | 0.247 | 3.1196 | [18.55, 47.98] |
| 11 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 20} training stress | 87 | 22 | 65 | -836.6882 | -8.3669 | 0.203 | 8.459 | [17.33, 35.33] |
| 12 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} training fold 1 | 52 | 24 | 28 | -287.3718 | -2.8737 | 0.425 | 2.8775 | [33.34, 59.5] |
| 12 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} training fold 2 | 35 | 11 | 24 | -301.1384 | -3.0114 | 0.247 | 3.1196 | [18.55, 47.98] |
| 12 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} training stress | 87 | 22 | 65 | -836.6882 | -8.3669 | 0.203 | 8.459 | [17.33, 35.33] |
| 13 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 35} training fold 1 | 102 | 38 | 64 | -691.4856 | -6.9149 | 0.257 | 6.9149 | [28.49, 46.94] |
| 13 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 35} training fold 2 | 78 | 25 | 53 | -644.8397 | -6.4484 | 0.213 | 6.5206 | [22.75, 43.04] |
| 13 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 35} training stress | 99 | 18 | 81 | -1005.7555 | -10.0576 | 0.11 | 10.0576 | [11.82, 26.92] |
| 14 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 35} training fold 1 | 101 | 37 | 64 | -666.0983 | -6.661 | 0.284 | 6.661 | [27.89, 46.36] |
| 14 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 35} training fold 2 | 78 | 25 | 53 | -652.3818 | -6.5238 | 0.203 | 6.596 | [22.75, 43.04] |
| 14 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 35} training stress | 104 | 19 | 85 | -1003.7033 | -10.037 | 0.145 | 10.037 | [12.02, 26.78] |
| 15 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 35} training fold 1 | 83 | 35 | 48 | -511.1707 | -5.1117 | 0.33 | 5.1117 | [32.12, 52.91] |
| 15 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 35} training fold 2 | 66 | 24 | 42 | -730.3177 | -7.3032 | 0.188 | 7.3744 | [25.81, 48.42] |
| 15 {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 35} training stress | 100 | 20 | 80 | -1030.2851 | -10.3029 | 0.155 | 10.3029 | [13.34, 28.88] |
| 16 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 1 | 83 | 35 | 48 | -511.1707 | -5.1117 | 0.33 | 5.1117 | [32.12, 52.91] |
| 16 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training fold 2 | 66 | 24 | 42 | -730.3177 | -7.3032 | 0.188 | 7.3744 | [25.81, 48.42] |
| 16 {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} training stress | 100 | 20 | 80 | -1030.2851 | -10.3029 | 0.155 | 10.3029 | [13.34, 28.88] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 5} reused later | 23 | 9 | 14 | -134.63 | -1.3463 | 0.327 | 1.641 | [22.16, 59.21] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 5} reused later | 23 | 9 | 14 | -115.7776 | -1.1578 | 0.423 | 1.641 | [22.16, 59.21] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 5} reused later | 19 | 9 | 10 | -46.697 | -0.467 | 0.632 | 0.9536 | [27.33, 68.29] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 5} reused later | 19 | 9 | 10 | -64.6676 | -0.6467 | 0.489 | 0.9836 | [27.33, 68.29] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 10} reused later | 40 | 18 | 22 | -276.82 | -2.7682 | 0.226 | 2.9125 | [30.71, 60.17] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} reused later | 40 | 18 | 22 | -283.6359 | -2.8364 | 0.206 | 2.9125 | [30.71, 60.17] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 10} reused later | 33 | 15 | 18 | -235.7019 | -2.357 | 0.169 | 2.4131 | [29.84, 62.01] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} reused later | 33 | 15 | 18 | -235.7019 | -2.357 | 0.169 | 2.4131 | [29.84, 62.01] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 20} reused later | 89 | 34 | 55 | -578.829 | -5.7883 | 0.277 | 5.9148 | [28.79, 48.59] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} reused later | 89 | 33 | 56 | -626.6817 | -6.2668 | 0.215 | 6.3271 | [27.77, 47.45] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 20} reused later | 76 | 30 | 46 | -609.3007 | -6.093 | 0.196 | 6.2487 | [29.25, 50.71] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} reused later | 76 | 30 | 46 | -609.3007 | -6.093 | 0.196 | 6.2487 | [29.25, 50.71] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.01, "threshold": 35} reused later | 155 | 52 | 103 | -980.4279 | -9.8043 | 0.242 | 9.8337 | [26.59, 41.3] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 35} reused later | 155 | 51 | 104 | -961.4834 | -9.6148 | 0.258 | 9.6443 | [26.0, 40.64] |
| {"family": "rsi2_reversion", "reward_risk": 1, "stop_fraction": 0.02, "threshold": 35} reused later | 136 | 48 | 88 | -765.1449 | -7.6514 | 0.29 | 7.8046 | [27.77, 43.63] |
| {"family": "rsi2_reversion", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 35} reused later | 136 | 48 | 88 | -763.4865 | -7.6349 | 0.292 | 7.788 | [27.77, 43.63] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation_folds.0 | -147.3276 | -1.4733 | not_available | not_available | not_available |
| candidates.0.validation_folds.1 | -160.6564 | -1.6066 | not_available | not_available | not_available |
| candidates.0.cost_stress | -437.2991 | -4.373 | not_available | not_available | not_available |
| candidates.1.validation_folds.0 | -168.8227 | -1.6882 | not_available | not_available | not_available |
| candidates.1.validation_folds.1 | -156.3692 | -1.5637 | not_available | not_available | not_available |
| candidates.1.cost_stress | -449.6321 | -4.4963 | not_available | not_available | not_available |
| candidates.2.validation_folds.0 | -147.3358 | -1.4734 | not_available | not_available | not_available |
| candidates.2.validation_folds.1 | -104.1386 | -1.0414 | not_available | not_available | not_available |
| candidates.2.cost_stress | -324.7581 | -3.2476 | not_available | not_available | not_available |
| candidates.3.validation_folds.0 | -147.3358 | -1.4734 | not_available | not_available | not_available |
| candidates.3.validation_folds.1 | -104.1386 | -1.0414 | not_available | not_available | not_available |
| candidates.3.cost_stress | -324.7581 | -3.2476 | not_available | not_available | not_available |
| candidates.4.validation_folds.0 | -306.7752 | -3.0678 | not_available | not_available | not_available |
| candidates.4.validation_folds.1 | -285.0106 | -2.8501 | not_available | not_available | not_available |
| candidates.4.cost_stress | -807.9802 | -8.0798 | not_available | not_available | not_available |
| candidates.5.validation_folds.0 | -289.2664 | -2.8927 | not_available | not_available | not_available |
| candidates.5.validation_folds.1 | -279.1916 | -2.7919 | not_available | not_available | not_available |
| candidates.5.cost_stress | -787.2347 | -7.8723 | not_available | not_available | not_available |
| candidates.6.validation_folds.0 | -159.9191 | -1.5992 | not_available | not_available | not_available |
| candidates.6.validation_folds.1 | -220.8294 | -2.2083 | not_available | not_available | not_available |
| candidates.6.cost_stress | -514.6211 | -5.1462 | not_available | not_available | not_available |
| candidates.7.validation_folds.0 | -153.3633 | -1.5336 | not_available | not_available | not_available |
| candidates.7.validation_folds.1 | -220.8294 | -2.2083 | not_available | not_available | not_available |
| candidates.7.cost_stress | -510.2334 | -5.1023 | not_available | not_available | not_available |
| candidates.8.validation_folds.0 | -448.6676 | -4.4867 | not_available | not_available | not_available |
| candidates.8.validation_folds.1 | -362.0295 | -3.6203 | not_available | not_available | not_available |
| candidates.8.cost_stress | -1009.8864 | -10.0989 | not_available | not_available | not_available |
| candidates.9.validation_folds.0 | -419.8057 | -4.1981 | not_available | not_available | not_available |
| candidates.9.validation_folds.1 | -356.3469 | -3.5635 | not_available | not_available | not_available |
| candidates.9.cost_stress | -1005.9426 | -10.0594 | not_available | not_available | not_available |
| candidates.10.validation_folds.0 | -287.3718 | -2.8737 | not_available | not_available | not_available |
| candidates.10.validation_folds.1 | -301.1384 | -3.0114 | not_available | not_available | not_available |
| candidates.10.cost_stress | -836.6882 | -8.3669 | not_available | not_available | not_available |
| candidates.11.validation_folds.0 | -287.3718 | -2.8737 | not_available | not_available | not_available |
| candidates.11.validation_folds.1 | -301.1384 | -3.0114 | not_available | not_available | not_available |
| candidates.11.cost_stress | -836.6882 | -8.3669 | not_available | not_available | not_available |
| candidates.12.validation_folds.0 | -691.4856 | -6.9149 | not_available | not_available | not_available |
| candidates.12.validation_folds.1 | -644.8397 | -6.4484 | not_available | not_available | not_available |
| candidates.12.cost_stress | -1005.7555 | -10.0576 | not_available | not_available | not_available |
| candidates.13.validation_folds.0 | -666.0983 | -6.661 | not_available | not_available | not_available |
| candidates.13.validation_folds.1 | -652.3818 | -6.5238 | not_available | not_available | not_available |
| candidates.13.cost_stress | -1003.7033 | -10.037 | not_available | not_available | not_available |
| candidates.14.validation_folds.0 | -511.1707 | -5.1117 | not_available | not_available | not_available |
| candidates.14.validation_folds.1 | -730.3177 | -7.3032 | not_available | not_available | not_available |
| candidates.14.cost_stress | -1030.2851 | -10.3029 | not_available | not_available | not_available |
| candidates.15.validation_folds.0 | -511.1707 | -5.1117 | not_available | not_available | not_available |
| candidates.15.validation_folds.1 | -730.3177 | -7.3032 | not_available | not_available | not_available |
| candidates.15.cost_stress | -1030.2851 | -10.3029 | not_available | not_available | not_available |
| fixed_later_comparisons.0.later_period | -134.63 | -1.3463 | not_available | not_available | not_available |
| fixed_later_comparisons.1.later_period | -115.7776 | -1.1578 | not_available | not_available | not_available |
| fixed_later_comparisons.2.later_period | -46.697 | -0.467 | not_available | not_available | not_available |
| fixed_later_comparisons.3.later_period | -64.6676 | -0.6467 | not_available | not_available | not_available |
| fixed_later_comparisons.4.later_period | -276.82 | -2.7682 | not_available | not_available | not_available |
| fixed_later_comparisons.5.later_period | -283.6359 | -2.8364 | not_available | not_available | not_available |
| fixed_later_comparisons.6.later_period | -235.7019 | -2.357 | not_available | not_available | not_available |
| fixed_later_comparisons.7.later_period | -235.7019 | -2.357 | not_available | not_available | not_available |
| fixed_later_comparisons.8.later_period | -578.829 | -5.7883 | not_available | not_available | not_available |
| fixed_later_comparisons.9.later_period | -626.6817 | -6.2668 | not_available | not_available | not_available |
| fixed_later_comparisons.10.later_period | -609.3007 | -6.093 | not_available | not_available | not_available |
| fixed_later_comparisons.11.later_period | -609.3007 | -6.093 | not_available | not_available | not_available |
| fixed_later_comparisons.12.later_period | -980.4279 | -9.8043 | not_available | not_available | not_available |
| fixed_later_comparisons.13.later_period | -961.4834 | -9.6148 | not_available | not_available | not_available |
| fixed_later_comparisons.14.later_period | -765.1449 | -7.6514 | not_available | not_available | not_available |
| fixed_later_comparisons.15.later_period | -763.4865 | -7.6349 | not_available | not_available | not_available |


#### grok-eth-evaluation.json

Status: archived_not_recomputed; SHA-256: `0fce373bbe0ce8efa2df2db21fed1282d404bee33d1b5c4986255c1acb9ee094`.

| Replay | Trades | Wins | Losses | Net P&L | Return % | PF | Max DD % | Win-rate 95% interval |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 10} training | 22 | 7 | 15 | -118.6474 | -1.1865 | 0.297 | 1.3894 | [16.36, 52.68] |
| 2 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 10} training | 21 | 7 | 14 | -125.9239 | -1.2592 | 0.285 | 1.462 | [17.19, 54.63] |
| 3 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 20} training | 41 | 14 | 27 | -216.2411 | -2.1624 | 0.352 | 2.1653 | [21.56, 49.45] |
| 4 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 20} training | 40 | 14 | 26 | -225.0004 | -2.25 | 0.343 | 2.2529 | [22.13, 50.49] |
| 5 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.01, "threshold": 30} training | 64 | 17 | 47 | -487.7085 | -4.8771 | 0.155 | 5.063 | [17.3, 38.48] |
| 6 {"family": "grok_consensus", "reward_risk": 2, "stop_fraction": 0.02, "threshold": 30} training | 59 | 15 | 44 | -480.7649 | -4.8076 | 0.136 | 4.9937 | [16.06, 37.8] |
| baseline | 63 | 20 | 43 | -45.8151 | -0.4582 | 0.958 | 3.3855 | [21.59, 44.0] |
| fixed_later | 73 | 16 | 57 | -507.6978 | -5.077 | 0.122 | 5.1321 | [13.97, 32.68] |
| fixed_cost_stress | 73 | 9 | 64 | -738.1841 | -7.3818 | 0.048 | 7.3818 | [6.62, 21.8] |

Descriptive phase comparisons. Training is never compared to a later baseline. Legacy input/cost identity is not independently certified.

| Metric phase | P&L minus cash | Return pp minus cash | P&L minus matching baseline | Return pp minus matching baseline | Baseline comparison |
| --- | ---: | ---: | ---: | ---: | --- |
| candidates.0.validation | -118.6474 | -1.1865 | not_available | not_available | not_available |
| candidates.1.validation | -125.9239 | -1.2592 | not_available | not_available | not_available |
| candidates.2.validation | -216.2411 | -2.1624 | not_available | not_available | not_available |
| candidates.3.validation | -225.0004 | -2.25 | not_available | not_available | not_available |
| candidates.4.validation | -487.7085 | -4.8771 | not_available | not_available | not_available |
| candidates.5.validation | -480.7649 | -4.8076 | not_available | not_available | not_available |
| fixed_later | -507.6978 | -5.077 | -461.8827 | -4.6188 | descriptive_same_archive_phase |
| fixed_cost_stress | -738.1841 | -7.3818 | not_available | not_available | not_available |
| baseline | -45.8151 | -0.4582 | 0.0 | 0.0 | descriptive_same_archive_phase |


## Limitations

- No independent evidence of improved profitability or future win probability
- Already-inspected datasets and archived searches are contaminated for inference
- No network requests, broker calls, funded accounts or automatic strategy deployment
- OHLC/assumed costs cannot reproduce real fills, swaps, corporate actions or liquidity
- Archived experiments are retained in full and explicitly not recomputed by this command
- Pine compilation, provider connectivity and external engine execution are separate checks
