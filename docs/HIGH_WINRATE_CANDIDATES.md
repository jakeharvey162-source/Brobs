# Open-source strategy candidates — audited claims, licensing and activation

BROBS now includes an **optional MIT-licensed Freqtrade strategy source** for local research. Neither the vendored strategy nor a third-party claim establishes 70–90% trading accuracy. Live-money execution is still disabled in BROBS.

## Candidate 1: BinHV45_Regime_5m (high *claimed* win rate; NOT copied)

Upstream: https://github.com/zevrichards/freqtrade-strategies
Source: `BinHV45_Regime_5m.py`.

The author's README reports **74.5% historical winning trades (314 trades), +22.53% return and 4.13% maximum drawdown** during a roughly six-month 5-minute crypto backtest. The same upstream CHANGELOG later reports **55.3% wins and -$301.24 across 85 forward dry-run trades** at one milestone. Its real implementation involves **5-minute entries**, **30-minute** pair-trend context, **1-hour** broader regime analysis, and specific Freqtrade exit/risk logic. It cannot be treated as compatible with BROBS's hourly backtests or forex results. Independent replication and later unseen periods remain outstanding.

**Licensing:** At this review, the GitHub repository does not declare a LICENSE. Public readability is not permission to redistribute its full source under BROBS's MIT license. No upstream strategy source was copied into BROBS. Its ideas, numbers and limitations are cited for research; request explicit author permission or select a properly licensed implementation before distributing copied source. If a license is subsequently added, recheck the license and exact Git revision.

## Candidate 2: TrendRider (MIT-licensed; copied as independent Freqtrade candidate)

Upstream: https://github.com/darkvolg/trendrider-strategy
Upstream strategy blob SHA: `66cfc02d3bd68bcd4709c07883882b92d5a1697e`.
Vendored exact source: `integrations/freqtrade/TrendRiderStrategy.py`.
Upstream license preserved: `integrations/freqtrade/TRENDRIDER-LICENSE` (Copyright 2026 TrendRider).

The upstream public source is a **1-hour crypto strategy** using EMA/RSI/ADX/MACD/volume/Bollinger indicators and extra multi-timeframe context. It has its **own** Freqtrade trading logic and depends on `freqtrade`, `pandas` and `talib`; it is **not called by BROBS's Python paper ledgers or TradingView Pine code**. Its published README compares a 30-day revision with prior versions but does not independently establish stable 70%+ winning trades. Upstream has separate commercial/private add-ons that are not bundled. An optional strategy being present does not itself alter profits.

Only the public MIT-licensed source was copied. No code runs automatically, no secrets are bundled, and no brokerage trade mode is switched on.

## Run TrendRider independently inside Freqtrade (paper/dry-run ONLY)

Use a supported **isolated Freqtrade dry-run environment**, not the BROBS production/paper database. Install the required packages according to Freqtrade's current setup instructions. Copy `integrations/freqtrade/TrendRiderStrategy.py` into the active Freqtrade `user_data/strategies/` directory.

Confirm its strategy class is `TrendRiderStrategy`, its timeframe is `1h` and that your Freqtrade configuration has `"dry_run": true`. The upstream strategy uses informative data for 4-hour and daily candles and BTC market context, so download the requisite historical timeframes and compatible market instruments. Then use Freqtrade commands along the lines of:

```bash
freqtrade list-strategies --userdir user_data
freqtrade backtesting --config user_data/config.json --strategy TrendRiderStrategy --timeframe 1h
freqtrade trade --config user_data/config.json --strategy TrendRiderStrategy --dry-run
```

Exact config paths, exchange integration and the strategy's runtime compatibility **are not verified** by BROBS CI. Do not supply any real credentials or set `dry_run: false` for this experiment. If your Freqtrade CLI does not accept `--dry-run` on `trade`, set it strictly in the config and verify before starting. Source copying and Python AST checks are not equivalent to running Freqtrade.

## Before BROBS promotes any external strategy

Required evidence (all still missing for this copy):
- Compatible live-market data, including necessary higher/lower timeframes and ticker histories
- No lookahead, future candles or selection bias, and an untouched chronological evaluation period
- Brokerage/venue-specific trading fees, spreads, slippage, partial fills, funding and minimum order size
- Enough independent closed trades to meaningfully bound win-rate uncertainty; net P&L and profit factor after costs
- Holdout and forward-paper results that improve on *the same* BROBS baseline with identical data and assumptions
- Actual risk control reliability through outages, stale quotes and liquidations
- No unexpected live execution or insecure secrets/network access

There is **no approved candidate**, no proven 80–90% win rate and no automatic strategy ensembling. Any later promotion must be justified by independent results, not by adding percentages from different studies.

## Helpful links

- Freqtrade official free strategy examples: https://github.com/freqtrade/freqtrade-strategies
- Freqtrade backtesting: https://www.freqtrade.io/en/stable/backtesting/
- BROBS legacy comparisons: `docs/PRO_COMPARISON.md`
- News source verification: `docs/NEWS_PROVENANCE.md`
