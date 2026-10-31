# BROBS loss-aware historical research — Astra handoff

Scope: paper-only historical diagnostics. This change does not modify the trading strategy, connect brokerage accounts, place orders, or claim future profitability.

## Implemented

- Opt-in include_trades=True on the existing forex replay exports all simulated closed trades. The default replay output remains unchanged.
- brobs.loss_lab uses earlier and later chronological price windows and runs the existing fixed strategy on separate paper ledgers.
- Training trades are described using only price observations before their entries. Trend and trailing volatility groups report realized wins, losses, combined P&L and exit reasons.
- At least eight training trades, more losses than wins and negative combined P&L creates a diagnostic review flag. It does not change orders or strategies.
- Optional CSV news metadata: published_at, available_at, source_url, event_label. An event is considered contextual only if publication and actual availability precede the trade.
- Tests check future-news exclusion, invalid timestamps, future-bar invariance, diagnostics and the previously reported EURUSD historical baseline.

## Run the tests and historical analysis

    python -m unittest discover -s tests -v
    python -m brobs.loss_lab --csv research/data/EURUSD_1h.csv --output brobs-loss-report.json

An optional --news-csv archived-events.csv argument supplies independently assembled archived metadata. No news is fabricated or fetched automatically. Without archived event metadata, the news count is zero.

## Important interpretation

The existing holdout is already inspected, not genuinely unseen. The repository reports 11 wins / 17 losses (39.29%) on 28 simulated EURUSD trades and a small positive return under documented assumptions. The new loss diagnostic does not attempt to manufacture a higher win rate.

Twenty of 28 wins is 71.4% observed, and 25 of 28 is 89.3% observed. Neither is a guarantee, and a high win fraction can coexist with negative returns. Overfitting past trade losses without independent forward evaluation can make a model worse.

News must be timestamped using when the system actually could access it. No model can reliably know an unannounced market-moving remark before it happens. Historical headline sentiment is not independently verified in this tool.

## Recommended Astra research roadmap

1. Run the full Python tests; compare the historical 28-trade count to the unchanged reference report. Investigate discrepancies rather than changing the expected values.
2. Audit data provenance, timestamp precision, duplicate candles, corporate actions, broker-specific costs and missing market news.
3. Extend read-only historical diagnostics to separately validated datasets for stocks and crypto without mixing currencies or broker assumptions.
4. Pre-register falsifiable hypotheses about loss regimes without changing execution rules. Keep fresh observations genuinely untouched for later testing.
5. Compare a fixed strategy, a simple baseline, and cash on new forward paper data. Report sample count, fees, drawdown, expectancy, failures and model uncertainty.
6. Build an educational decision-review screen that shows the evidence that existed at each trade and the outcome, but prevents post-event facts from entering earlier decisions.
7. Maintain TradingView as a separate chart and paper-simulation surface: Python code and large-model research agents do not run directly inside Pine.

## Limits

This release is offline/paper-only. Its training review flags do not auto-adapt or trade. The historical forex replay omits swaps, liquidity and some broker execution behavior. Passing software tests is not evidence of reliable future earnings.


## Follow-up: controlled loss-screen shadow experiment (31 October 2026)

The original PR #4 is merged. The separate \`brobs.independent_validation\` experiment now tests a **frozen, training-derived** veto against the unmodified forex replay, without changing the default signals, order APIs or risk parameters. A veto can affect **new entries only**; existing-position management and protective exits remain with \`FXBook\`. For every tested later period the report includes:

- Baseline and loss-screen paper closed trades, wins, losses, break-even trades, P&L, returns, profit factor and max drawdown.
- A higher-cost baseline and higher-cost screen (0.0003 spread, commission_fraction 0.00005), the number of entry signals screened, and an explicit failure/inconclusive label.
- OHLCV chronology/range checks and descriptive timestamp-gap counts. Gaps are never filled by invented bars. Historical data source integrity must still be independently established.
- Contextual news rows are accepted only when **published and actually available strictly before** an entry. Same-timestamp observations are excluded conservatively.
- No automatic promotion, no trading-policy changes, no online fitting and no live-money path.

Run: \`python -m brobs.independent_validation --csv research/data/EURUSD_1h.csv --output /tmp/brobs-independent-validation.json\`

The code deliberately sets \`improved_win_rate_verified=false\`. Even a numerically better shadow return is an **exploratory comparison on a previously inspected** later interval. No new independent trading history is supplied, and the program must not present the result as confirmed out-of-sample improvement. Costs are represented in spread/slippage/commission assumptions and scenario P&L, **not** an auditable breakdown of each realized fee.

**Preserved published benchmarks, not new measurements:** the original EUR/USD fixed multi-agent reference has 28 closed trades (11 wins, 17 losses), +0.2923% return and 0.1906% maximum drawdown; its higher-cost run returned +0.1663%. The separate multi-market default-trend research logged EUR/USD 28 (11/17, +0.2810%), AAPL 8 (6/2, +3.9589%), BTC/USDT 55 (15/40, -1.2204%) with recorded cost-stressed returns of +0.0886%, +3.8034%, and -2.7066% respectively. Thirty explored multi-market candidates produced **zero qualified replacements**. These datasets, models, currencies and sample sizes cannot legitimately be pooled to assert an edge.

Further independent evaluation requires **new prospectively frozen paper observations**, vendor-matched executable quotes and fee records, archived-news provenance verified separately from the model, and enough comparable outcomes for uncertainty and drawdown analysis. The BTC archive candles are not committed, so CI cannot independently reproduce that archive without reacquisition and checksum verification. The AAPL dataset is an old, unadjusted daily series. Failed hypotheses must remain visible.
