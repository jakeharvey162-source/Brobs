# Expanded market evaluation — 9 October 2026 (Johannesburg)

**No reliable 70–80% win rate was established.** Thirty additional train-validation candidates were tested across forex, stocks and crypto, after the earlier twelve-variant experiment. Candidates used standard RSI pullback, RSI2 mean reversion, Donchian breakout and trend/momentum rules. None met the minimum validation trade/profit gates; none was automatically promoted.

| Default trend benchmark | Later-period closed trades | Wins / losses | Win rate | Net return | Higher-cost return |
|---|---:|---:|---:|---:|---:|
| EUR_USD | 28 | 11 / 17 | 39.29% | +0.2810% | +0.0886% |
| AAPL | 8 | 6 / 2 | 75.0% | +3.9589% | +3.8034% |
| BTC_USDT | 55 | 15 / 40 | 27.27% | -1.2204% | -2.7066% |

The stock result exceeds 70% numerically, but only eight trades and an old daily sample do not establish a durable target. The BTC default lost money; it is a paper research option, not a profitable strategy recommendation. Keeping cash would have outperformed this crypto sample. The forex final period was already examined in previous work, so it cannot be presented as pristine unseen data. Stock/crypto samples were not used to select parameters on their final 30%; repeated selection still adds overfitting risk.

All candidate metrics and selection rules are committed in `research/*-strategy-evaluation.json`. Selection uses the last 40% of the initial 70% of each series, requires 30+ closed validation trades, positive net P/L and profit factor >=1.2, then ranks eligible strategies by observed win rate. Ten candidates per market are disclosed. Stop/target ratios are 1.5:1 or 2:1, not a tiny target designed to manufacture a high percentage.

The accounting engine uses completed past bars, next-bar-open fills, explicit bid/ask, commission, slippage, no leverage and stop-first treatment of ambiguous bars. Every final position is liquidated. Replay uses the same transactional engine in an in-memory SQLite connection for speed; the original committed forex report reproduces byte-for-byte. Crypto is USDT; stock/FX is USD; returns are not pooled. Daily equity anchors, risk halts and distinct quantity rules remain active. The comparison benchmark uses actual runner default stop/target parameters.

Samples: EURUSD 3,162 hourly bars (2026); AAPL 506 daily bars (2015–2017, raw unadjusted OHLCV); BTCUSDT 6,552 hourly bars January–September 2026, downloaded directly from Binance and checksum verified. The crypto final period begins 2026-07-11 02:00 UTC. No swaps, dividends/corporate-action accounting, settlement, liquidity constraints or partial fills are modeled. Data integrity checks do not validate future odds.

## Public-project research

- Freqtrade strategies: https://github.com/freqtrade/freqtrade-strategies — inspected README and TrendRiderStrategy. Its author describes strategies as starting points, not guaranteed profitable systems. No Freqtrade source copied or strategy performance claims accepted as evidence.
- Freqtrade lookahead-analysis: https://www.freqtrade.io/en/stable/lookahead-analysis/ — motivates prefix-only signal tests and refusal to use precomputed future indicators. Freqtrade itself is not installed into this standard-library app.
- QuantConnect LEAN: https://github.com/QuantConnect/Lean — inspected MeanReversionPortfolioAlgorithm and research guidance; modular signal/risk/accounting separation. This release does not pretend LEAN is the BROBS execution engine.
- Backtrader: https://github.com/mementum/backtrader — existing optional real Backtrader baseline remains available. Different cost/bracket assumptions preclude a superiority claim.

## Integration and verification

- Unit/regression suite: 99 tests, including new whole-share/fractional sizing, no spot shorting, profile/currency isolation, persistence, fee reconciliation, concurrent deduplication, stop processing with missing history, stock market-closed behavior, completed-bar exclusion and checksum failures.
- Browser user flows: desktop 1280px and mobile 390px rendering, API refresh, positions and account-currency checks passed for forex, stocks and crypto, with zero JavaScript errors.
- Latest upstream forex input-guard changes and duplicate-pair regression tests preserved.
- Binance public snapshot and 499 completed hourly candles were retrieved. A complete local-paper tick returned `paper` with a HOLD signal and no fills, as the votes did not agree. This verifies data/decision/account integration, not a broker fill or profit.
- Slow-request clock bug fixed: fresh quotes are now checked at execution time after requests, while explicit replay/test clocks stay deterministic.
- Stock data adapter tested with fixtures; a real credentialed Alpaca session remains unverified. Existing OANDA credentialed verification limitation also remains.
- Pine is a v6 implementation reviewed against official documentation, not compiled or account-tested in TradingView here. Notification setup does not deploy a webhook or connect real-money orders.

## What remains for the win-rate target

More fresh forward-paper trades with frozen parameters, independent feeds, other symbols/regimes, broker-matched costs and realistic operational failures are necessary. There is no honest way to guarantee that further searching will yield 70–80%. A failed candidate should be rejected rather than relabeled successful. The added workflows make these experiments reproducible without paid AI APIs.
