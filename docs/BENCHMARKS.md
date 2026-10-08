# Benchmarking BROBS honestly

Run: `python -m brobs.compare --csv real_prices.csv --market crypto --symbol BTCUSD > comparison.json`

The comparison runs the SMA strategy, multi-agent strategy, buy-and-hold (including estimated entry/exit costs), and cash over the same final 30% of the supplied history. The first 70% is not used to optimize either strategy; 21 preceding bars warm up the indicators. The strategies use paper fills with estimated fees/slippage, not actual broker fills.

This is a *basic holdout smoke comparison*, not proof of outperformance. There is no data automatically downloaded, no tested profitability ratio, no professional trader benchmark, and no external repository strategy benchmark yet. To claim an advantage, run multiple assets, market regimes, rolling walk-forward windows, transaction-cost stress tests, survivorship-bias-aware data and months of forward paper trading. Record win rate, profit factor, Sharpe, max drawdown and net after-cost returns on independent periods. Reject strategies that beat cash only by overfitting.

For more mature research tools, assess LEAN's market modeling and Freqtrade's lookahead-analysis and dry-run features. These projects are **not installed or embedded** in BROBS yet.
