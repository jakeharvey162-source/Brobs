# BROBS comparison and measured upgrade

BROBS is a stronger local paper-research app after this update, but it has not demonstrated a profitable 70% strategy or superiority to Freqtrade/LEAN. Those projects are engines and operating frameworks, not fixed win-rate products. Comparing headline percentages from unrelated bots is not a valid benchmark.

## What is now implemented

- Three additional independent strategy families: `band_recovery`, `range_reversion`, and `macd_swing`. Both band families require expected distance to their moving mean to exceed twice the estimated roundtrip cost. That distance is a setup filter, not a prediction.
- A bounded ten-configuration strategy lab with two chronological validation windows, cost stress, prefix-only feature calculations, a default-strategy baseline and explicit cash fallback. Candidates are declared before their later-period comparison; later winners do not determine selection.
- An optional research-evidence gate in both runners. A missing, rejected, malformed, non-finite or mismatched report blocks new entries. It cannot suppress exits or override sizing. It is a trusted local file check, not independent verification of a file's claimed results.
- Persisted per-instrument cooldown and consecutive-loss guards, enforced inside the ledger transaction. Restarts do not remove the policy. They apply to entries only and default to off; their profitability has not been established.
- Forex signal/account-history errors now trigger a separate fresh-quote stop/risk check for existing local paper positions before the original error is reported. Stale or unavailable quotes never fabricate a close. Signal failure cannot open new positions.
- Pause/resume now uses the database's saved configuration, so the dashboard's pause command works on accounts with custom risk/stop settings.
- The dashboard shows net expectancy, average win/loss, loss streaks, entry guards and actual agent explanations. Its last 250 equity ticks persist across restarts. USD and USDT remain separate.

## Comparison with established projects

This compares documented capabilities with tested BROBS behavior; Freqtrade and LEAN were not installed as execution engines.

| Area | Established reference | BROBS after this update | Remaining gap |
|---|---|---|---|
| Research selection | QuantConnect documents walk-forward optimization and overfitting controls | Two training validation folds, stressed execution costs, later-period comparisons, cash fallback | Many historical periods have already been inspected; genuinely new forward evidence is still needed |
| Leakage checks | Freqtrade has dedicated lookahead analysis | Replay sees only previous bars; feature-cache prefix stability and next-open ordering tested | No full Freqtrade-style sliced-run audit across every strategy |
| Entry protections | Freqtrade offers cooldown, stop-loss and drawdown protections | Durable cooldown, consecutive-loss guard, existing daily-loss and drawdown halts | Consecutive-loss guard is an independent design, not an exact Freqtrade StoplossGuard implementation |
| Fill realism | LEAN has brokerage-specific fill/slippage models; Freqtrade can use finer intrabar data | Bid/ask costs, fixed slippage/fees, next-open entries, conservative stop-first OHLC replay | No order-book impact, partial fills, exchange-specific lot/minimum-notional models or intrabar tick replay |
| Execution | Mature projects provide execution integrations | Read-only public crypto/OANDA-practice/Alpaca-data adapters and durable local paper ledger | No actual broker-paper orders, order reconciliation or real-money execution |
| Monitoring | FreqUI provides bot monitoring and controls | Local read-only dashboard, persisted curve, detailed votes, performance/risk metrics, matching pause command | No hosted authenticated multi-user control plane, unattended service supervision or phone notifications |
| Prediction | Model/framework availability does not prove a trading edge | Optional local ML and Grok review; no paid model call in this work | Neither AI option has demonstrated an out-of-sample edge; no verified news/funding feed |

Primary references reviewed: [Freqtrade protections](https://www.freqtrade.io/en/stable/plugins/), [lookahead analysis](https://www.freqtrade.io/en/stable/lookahead-analysis/), [backtesting assumptions](https://www.freqtrade.io/en/stable/backtesting/), [FreqUI](https://www.freqtrade.io/en/stable/freq-ui/), [QuantConnect research guide](https://www.quantconnect.com/docs/v2/writing-algorithms/key-concepts/research-guide), [walk-forward optimization](https://www.quantconnect.com/docs/v2/writing-algorithms/optimization/walk-forward-optimization), and [fill models](https://www.quantconnect.com/docs/v2/writing-algorithms/reality-modeling/trade-fills/key-concepts). [Freqtrade's public BbandRsi example](https://github.com/freqtrade/freqtrade-strategies/blob/main/user_data/strategies/berlinguyinca/BbandRsi.py) was inspected as a mathematical reference. No third-party strategy code was copied; BROBS variants differ in regime, recovery, costs and risk rules.

## Actual test results

The lab tested ten configurations on each of three datasets: four band variants, two MACD stop variants, and the existing trend, RSI14 pullback, RSI2 reversion and Donchian families. It requires **each** of two training validation folds to have at least 15 closed trades, positive net P/L and profit factor >=1.1, plus positive combined stressed-validation P/L. Ranking prioritizes worst-fold net return, not win rate. None qualified on any dataset.

| Dataset | Bars / history | Later default win rate | Later default net return | Lab's train-selected choice |
|---|---|---:|---:|---|
| BTC/USDT | 15,312 hourly bars, January 2025–September 2026 | 31.86%, 113 trades | -4.5641% | Cash; no candidate qualified |
| ETH/USDT | 6,552 hourly bars, January–September 2026 | 31.75%, 63 trades | -0.4582% | Cash; no candidate qualified |
| EUR/USD | 3,162 hourly bars, March–September 2026 | 39.29%, 28 trades | +0.2810% | Cash; no candidate qualified |

The last 30% of each series is the later comparison. BTC later data starts March 23, 2026; ETH July 11; EUR/USD August 3. A cash simulation earns 0% here, before inflation/interest; it has no trades and no win rate. Its apparent improvement over losing BTC/ETH defaults is loss avoidance in this historical test, not a profitable predictor. The default runners still use `trend` unless a strategy/gate is explicitly selected.

Some later results appear impressive with too little evidence: EUR/USD RSI14 pullback won 4 of 5 trades (80%), EUR/USD band recovery 2 of 2 (100%), and ETH band recovery 4 of 5 (80%). These were **not selected** and cannot establish 70–80% performance. Range reversion on EUR/USD won 54.17% of 24 trades but returned -0.2908%, illustrating why a higher win rate is not sufficient.

The 2026 datasets were examined in earlier work. New 2025 BTC history expands the sample; it does not make repeatedly examined 2026 outcomes an untouched holdout. Stocks remain supported in the runner, including the new strategies and entry guards, but the old 506-bar daily AAPL sample is insufficient for this 600-bar-minimum lab. Credentialed current stock data and corporate-action-aware equity validation remain outstanding.

The actual Backtrader 1.9.78.123 engine was rerun on the EUR/USD sample: its existing SMA baseline returned +0.2950%, 35.42% wins on 48 closed trades, and 0.3642% maximum drawdown. This uses different spread, bracket and liquidation assumptions, so it does **not** prove BROBS beats or loses to Backtrader. The cost-consistent strategy comparisons are the BROBS lab's internal runs.

Full reports: `research/lab-btc-evaluation.json`, `research/lab-eth-evaluation.json`, `research/lab-forex-evaluation.json`, and `research/backtrader-current-reference.json`. Official archive checksums and normalized combined-input hashes are retained in `research/data/BTCUSDT_2025_2026.provenance.json`. Raw downloaded crypto history is not redistributed.

## Run the stronger paper workflow

From the repository root, use a fresh database and keep the connected runner running:

```bash
python -m brobs.market_runner --market crypto --symbols BTC_USDT --db guarded_crypto.db --evidence-report research/lab-btc-evaluation.json --cooldown-seconds 3600 --loss-streak-limit 3 --loss-window-seconds 86400
python -m brobs.app --market crypto --db guarded_crypto.db --port 8767
```

The supplied BTC report currently has no accepted candidate, so this workflow blocks new entries. It can still mark and close already-stored positions. The gate checks market, instrument, exact strategy/threshold/stop/reward settings, 100+ later trades, positive later/stressed P/L, PF>=1.2 and three profitable later folds. No current report meets these requirements. It never promotes a strategy automatically.

For forex, use `python -m brobs.fx_runner --pairs EUR_USD --db guarded_fx.db --evidence-report research/lab-forex-evaluation.json --cooldown-seconds 3600 --loss-streak-limit 3`. OANDA practice credentials are required for its real-price feed. The recovery path checks local paper stops; it does not place an OANDA order.

To research a specific family without the evidence gate, use a **separate** database and explicit parameters:

```bash
python -m brobs.market_runner --market crypto --symbols ETH_USDT --strategy range_reversion --threshold 35 --stop 0.02 --reward-risk 2 --db experimental_eth.db
```

This variant is experimental and has not passed the selection gates. Do not interpret its name or availability as a recommendation. Add `--demo --once` only for a synthetic smoke test. Forex's added families require H1 bars. Both runners accept `--threshold`, `--stop`, `--reward-risk` and the optional protection settings; persisted risk configuration must match on restart. Protections remain saved when omitted from later CLI invocations. Disable them explicitly with `--cooldown-seconds 0 --loss-streak-limit 0`.

Pause/resume with the matching database:

```bash
python -m brobs.market_runner --market crypto --db guarded_crypto.db --pause
python -m brobs.market_runner --market crypto --db guarded_crypto.db --resume
```

Keep polling for exits while entries are paused. If quotes are unavailable, no software stop can guarantee a fill. The dashboard remains loopback-only; this update does not turn it into a public service.

## Reproduce the research for zero API spend

Public Binance archives require no key. Download the 2025 and 2026 periods separately, then merge canonically so the combined CSV hash matches the report:

```bash
python -m brobs.public_data --symbol BTCUSDT --months 2025-01 2025-02 2025-03 2025-04 2025-05 2025-06 2025-07 2025-08 2025-09 2025-10 2025-11 2025-12 --output local-data/BTCUSDT_2025.csv
python -m brobs.public_data --symbol BTCUSDT --months 2026-01 2026-02 2026-03 2026-04 2026-05 2026-06 2026-07 2026-08 2026-09 --output local-data/BTCUSDT_1h.csv
python -m brobs.history_merge --inputs local-data/BTCUSDT_2025.csv local-data/BTCUSDT_1h.csv --output local-data/BTCUSDT_2025_2026.csv
python -m brobs.strategy_lab --csv local-data/BTCUSDT_2025_2026.csv --market crypto --symbol BTC_USDT --output local-data/lab-btc-evaluation.json
python -m brobs.strategy_lab --csv research/data/EURUSD_1h.csv --market forex --symbol EUR_USD --output local-data/lab-forex-evaluation.json
python -m unittest discover -s tests -v
```

Use the ETH download command in [GROK.md](GROK.md), followed by `brobs.strategy_lab --market crypto --symbol ETH_USDT`, for its report. Running the optional Backtrader reference requires separately installing its pinned dependency. All new strategy/research/protection code uses the Python standard library. No paid APIs, private third-party keys or model credits were used.

Validation completed: 125 automated tests; desktop and 390px mobile browser flows for all three profiles, correct currencies, refresh and zero JavaScript errors; earlier reversion/stock research reports reproduced unchanged; deterministic EUR/USD lab reproduction is included in CI. Real xAI/OANDA/Alpaca authenticated sessions, actual brokerage paper fills and TradingView compilation remain unverified. The new Python families are not in the existing Pine script; see [TRADINGVIEW.md](TRADINGVIEW.md) for its current scope.
