# Freqtrade / HyperGrok integration report

## Exact scope

Two unique upstream repositories were supplied (HyperGrok appeared twice). Complete upstream code is referenced through pinned git submodules:

- `external/freqtrade`: `freqtrade/freqtrade` at `2cdfc2325e3c2af1680e8adbe5245ac42709fda9`, GPL-3.0.
- `external/hypergrok-trading-desk`: `galleonlabs/hypergrok-trading-desk` at `735e5c88697f5d381b919c20c9c882469527c024`, MIT.

Both complete repositories were checked out locally at these pins. To obtain all their source yourself, clone with `git clone --recurse-submodules https://github.com/jakeharvey162-source/Brobs.git`, or use `git submodule update --init --recursive` in an existing clone. GitHub ZIP downloads do not include submodule contents. The current work inspected repository trees, Freqtrade's strategy template and HyperGrok's risk-manager role/licence; it did not audit every upstream file. Complete projects are preserved without misrepresenting them as one merged trading engine. Freqtrade remains a separate GPL engine; the original Freqtrade adapter is offered under GPL-3.0-only with its licence in `integrations/freqtrade/LICENSE`. Copied HyperGrok role text retains its MIT licence and attribution.

`integrations/freqtrade/BrobsStrategy.py` connects BROBS trend/momentum/volatility entry/exit signals to Freqtrade's v3 strategy API for long-only hourly spot crypto. It uses a 2% stop, 4% ROI target and a capped stake callback. `dry-run.json` uses an initial 10 USDT, one position, empty credentials and disabled remote control. Exchange minimum stake is respected: a minimum above the capped budget rejects entry instead of increasing risk. At $10, the 20% notional budget is only about $2, so an exchange's minimum order may block every entry. The fee/slippage reserve is an assumption, not an exchange-specific cost guarantee.

`integrations/hypergrok/risk-manager.md` contains the actual upstream risk-manager role, with attribution. It requires the external Grok Bot workspace/runtime and referenced skills to operate. It is not a running BROBS AI. The submodule exposes the rest of the desk; no agent or wallet has been deployed.

## Use the optional engine

Install Freqtrade using its official installation instructions in a separate environment. From the BROBS repository root, make `brobs` importable with `PYTHONPATH` (PowerShell: `$env:PYTHONPATH=(Get-Location).Path`). Then:

```bash
freqtrade create-userdir --userdir user_data
freqtrade list-strategies --strategy-path integrations/freqtrade --config integrations/freqtrade/dry-run.json
freqtrade download-data --config integrations/freqtrade/dry-run.json --timeframes 1h --timerange 20250101-20261001
freqtrade backtesting --config integrations/freqtrade/dry-run.json --strategy BrobsStrategy --strategy-path integrations/freqtrade --timerange 20260323-20261001
freqtrade trade --config integrations/freqtrade/dry-run.json --strategy BrobsStrategy --strategy-path integrations/freqtrade
```

These are Freqtrade commands; the last starts its own dry-run engine, not BROBS's existing dashboard. Feed availability, region restrictions, engine version and minimum order values may prevent operation. Do not run competing engines against one funded account. Freqtrade execution differs from BROBS's OHLC replay, so existing win rates must not be labelled Freqtrade results.

## What the results establish

Signal prefix/parity and sizing tests verify the independent adapter calculations. Python tests do not prove end-to-end exchange execution, profitability or Grok quality. The previous default-strategy later-period BROBS reports show BTC 36/113 wins (31.86%, -4.5641% net return), ETH 20/63 (31.75%, -0.4582%), EURUSD 11/28 (39.29%, +0.2810%). These are historical BROBS simulations, not freshly measured combined-engine performance. The 48 newer RSI2 comparisons failed acceptance. Future win probability and combined-system prediction accuracy remain unknown; no measured 70% edge is established. Imported prompts and execution frameworks do not change those statistics by themselves.

### Actual Freqtrade engine results

Installed Freqtrade 2026.9 in an isolated runtime. Its configuration validates and its strategy loader reports `BrobsStrategy: OK`. The pinned upstream develop source and the tested PyPI engine version are recorded separately; the complete upstream test suites were not run. The initial direct backtest failed on unavailable Binance market-metadata access. The offline checker then ran the real engine with downloaded hourly BTC/ETH candles and explicit synthetic spot rules: 5 USDT minimum cost, 0.000001 unit step, 0.01 price tick. It refuses socket connections during the run. These constraints are assumptions, not verified current exchange specifications.

| Engine replay | Initial capital | Closed trades / wins / losses | Win rate | Net return | Profit factor | Max account drawdown |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Base: 0.1% fee per fill | 10,000 USDT | 132 / 47 / 85 | 35.61% | +5.4028% | 1.3082 | 2.8628% |
| Stress: 0.2% fee per fill | 10,000 USDT | 129 / 42 / 87 | 32.56% | -0.3498% | 0.9823 | 5.3479% |
| Small account: 0.1% fee | 10 USDT | 0 / 0 / 0 | Not applicable | 0% | Not applicable | 0% |

This is one shared long-only BTC/ETH portfolio with one open position, March 23–September 30, 2026. The 10-USDT replay cannot enter because the 20% notional cap is below the assumed exchange minimum. Explicit spread/slippage, order-book impact, live latency, BROBS daily-loss/cooldown rules and Grok/news vetoes are absent from this adapter replay. Costs doubling removes the observed profit. The periods have already been examined: this is exploratory evidence, not independent validation or a live profitability claim. Neither real broker/exchange fills nor a deployed HyperGrok runtime were tested.

Reproduce after installing `freqtrade==2026.9` and making BROBS importable:

```bash
python scripts/freqtrade-offline-check.py --btc /path/to/BTCUSDT_2025_2026.csv --eth /path/to/ETHUSDT_1h.csv --output /tmp/freqtrade-base.json
python scripts/freqtrade-offline-check.py --btc /path/to/BTCUSDT_2025_2026.csv --eth /path/to/ETHUSDT_1h.csv --fee 0.002 --output /tmp/freqtrade-stress.json
python scripts/freqtrade-offline-check.py --btc /path/to/BTCUSDT_2025_2026.csv --eth /path/to/ETHUSDT_1h.csv --capital 10 --output /tmp/freqtrade-ten.json
```

All 151 local BROBS tests passed, and the three real-engine offline replays completed. Recorded reports include trade-level P/L, exact data hashes and limitations in `research/freqtrade-*-evaluation.json`. The optional ML classifier's existing historical accuracy is 50.74%, below its 53.38% majority baseline; that is not the combined engine's accuracy or a trading edge.

## Real-money activation

There is no supported real-money activation switch in BROBS's Python runners. Its OANDA order gateway is practice-only. Freqtrade, as a separate product, documents production operation with a supported exchange account, appropriately scoped local API credentials, a separate live database and `dry_run: false`. HyperGrok describes a mainnet Hyperliquid API-wallet setup in its upstream runbook. Those are separate systems, not evidence that BROBS is ready or profitable. No live configuration, funded wallet or order has been activated here. Credentials belong in local private configuration/environment variables, never GitHub, Pine scripts or chat.

## TradingView

Use `tradingview/BROBS.pine`: copy Raw code, open a normal 1-hour chart, open Pine Editor → Open → Templates → New strategy, replace the template, save and Add to chart. Set initial capital and realistic fees/slippage in Properties; inspect Strategy Tester. Notifications use Order fills only with `{{strategy.order.alert_message}}`. Freqtrade and HyperGrok cannot be pasted into Pine Editor; they run outside TradingView. Pine compilation is not verified here. Full instructions: `docs/TRADINGVIEW.md`.

Primary sources: https://github.com/freqtrade/freqtrade ; https://github.com/galleonlabs/hypergrok-trading-desk ; https://www.freqtrade.io/en/stable/configuration/ ; https://www.freqtrade.io/en/stable/strategy-callbacks/ .
