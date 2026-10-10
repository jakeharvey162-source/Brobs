# BROBS AI

Forex research and autonomous **local paper trading**. Real-money execution is disabled. No guaranteed returns.

See [execution status and engine comparison](docs/EXECUTION_STATUS.md) for the separately tested OANDA practice-entry gateway, broker protection confirmation, remaining automation gaps and exactly which public projects were used. This gateway is not yet connected to the polling runner or dashboard.

The new [Freqtrade/HyperGrok integration report](docs/REPO_INTEGRATION.md) covers the complete pinned upstream submodules, optional Freqtrade strategy adapter, attributed HyperGrok risk role and actual offline engine backtests. The optional Freqtrade engine has its own account/reporting; it is not connected to this dashboard.

The app polls OANDA's practice-data API, evaluates trend/momentum/volatility votes, simulates trades locally and persists positions, trades and decisions in SQLite. It does **not** submit orders to OANDA, and its local paper balance is separate from the broker account balance.

## Run now — no account required for a labeled demo

Requires Python 3.11 or newer. No core dependencies.

```bash
python -m unittest discover -s tests -v
python -m brobs.fx_runner --demo --once --db demo_fx.db
python -m brobs.app --db demo_fx.db
```

Open **http://127.0.0.1:8767**. To keep the synthetic runner active, omit `--once` in another terminal. Demo data and results are explicitly labeled synthetic.

## Real practice-market data

Configure an eligible OANDA v20 **practice** account locally. In PowerShell:

```powershell
$env:OANDA_PRACTICE_TOKEN = "YOUR_PRACTICE_TOKEN"
$env:OANDA_PRACTICE_ACCOUNT = "YOUR_PRACTICE_ACCOUNT_ID"
python -m brobs.fx_runner --pairs EUR_USD GBP_USD --db brobs_fx.db
```

In a second terminal:

```bash
python -m brobs.app --db brobs_fx.db
```

The practice account currency must be USD. EUR_USD, GBP_USD, AUD_USD and NZD_USD are supported. Quotes must be fresh and tradeable. The runner checks completed candles, current executable bid/ask and all open-position marks. Invalid data creates no new trades. This integration has been fixture-tested; a real credentialed OANDA session has **not** been verified in the development environment.

## Emergency stop for TradingView paper alerts

The TradingView alert receiver is **paper only**. To prevent new entries quickly when an operator notices suspicious trades, configure a local pause marker before starting it:

```powershell
$env:BROBS_ALERT_PAUSE_FILE = "C:\\brobs\\paper-stop.marker"
python -m brobs.alerts
```

Creating that marker blocks **new paper buy alerts**. Previously open paper positions can still receive sell/exit alerts. Stale buy events received while paused are consumed rather than executed later.

```powershell
New-Item -Path "C:\\brobs\\paper-stop.marker" -ItemType File
# After human review and confirmation only:
Remove-Item -Path "C:\\brobs\\paper-stop.marker"
```

This is a **local paper-entry kill switch**, not a brokerage emergency liquidation control. It cannot cancel actual broker orders, guarantee exits, or prove a strategy is profitable. The marker must be created on the machine running the alert receiver. It is available without a paid API.

## Risk controls

Default: $10,000 paper capital, 0.5% risk budget per entry, 0.5% stop distance, 2:1 take-profit distance, at most 20% of NAV notional per pair, no leverage, 2% daily equity-loss halt and 10% peak drawdown halt. Position sizing also reserves full notional, so the risk budget is a cap rather than a target.

```bash
python -m brobs.fx_runner --capital 10000 --risk 0.005 --daily-loss 0.02 --db brobs_fx.db
python -m brobs.fx_runner --pause --db brobs_fx.db
python -m brobs.fx_runner --resume --db brobs_fx.db
```

Reuse the same custom settings when operating that database. Configuration mismatch fails closed; use a new DB for a different experiment. Pause blocks new entries while a running poller still manages stops. A max-drawdown halt stays latched; resume does not clear it. Daily halts reset on the next UTC day.

Stops are evaluated on polls. Gaps, outages and stopping the runner can exceed configured loss thresholds. Swaps/rollover, liquidity, partial fills and broker margin/liquidation are not modeled. Keep this app local; no public authentication or deployment is supplied.

## Reproduce historical evidence

An MIT-licensed public EURUSD hourly evaluation sample is included with attribution. It is vendor-supplied historical data, not an independently certified feed.

```bash
python -m brobs.fx_research --csv research/data/EURUSD_1h.csv --output research/eurusd-holdout.json
pip install -r requirements-research.txt
python -m brobs.reference --csv research/data/EURUSD_1h.csv
```

The 949-bar chronological holdout produced **11 wins / 17 losses, 39.29% observed win rate, +0.2923% simulated return**, using the stated spread/slippage assumptions. Larger-cost stress returned +0.1663%. One of three holdout subperiods lost money. Only 28 closed trades: insufficient evidence of a durable edge. Swaps could materially change these small returns.

The simpler SMA strategy in the same simulator returned +0.2517%. The actual optional Backtrader SMA baseline returned +0.2950%; its brackets/cost assumptions differ, so this is not a superiority test. See [validation report](docs/VALIDATION.md) and [benchmark JSON](research/eurusd-holdout.json).

## Local AI research

The default agents are deterministic research rules. Optional `--ml-veto` uses a local scikit-learn logistic classifier. It trains on past bars, evaluates a chronological holdout, abstains if it does not beat the majority baseline, and can veto a contrary directional signal. No paid API is required. This optional variant is **not** included in the default trading benchmark.

The model tested at 50.74% direction accuracy against a 53.38% majority baseline, so no prediction advantage is established. Classification accuracy is not a win rate or trading return.

## Existing interfaces

`brobs.forex_runner` remains the legacy research-only runner; `brobs.forex_dashboard` is its legacy ledger viewer. Use `brobs.fx_runner` and `brobs.app` for the new FX simulator. Crypto/stock research modules are preserved. TradingView's existing localhost gateway is a separate demo; forex midpoint-only alerts are rejected. No live order endpoint exists.

## TradingView and win-rate research

Paste [`tradingview/BROBS.pine`](tradingview/BROBS.pine) into TradingView Pine Editor for EURUSD H1 strategy testing and paper notifications. Follow [installation and alerts](docs/TRADINGVIEW.md). The [70–80% improvement experiment](docs/WIN_RATE_RESEARCH.md) failed later-period checks; the default strategy is retained. A reliable target win rate is not established.

## Stocks and crypto added

The same durable paper accounting now supports separate **stock/USD** and **crypto/USDT** accounts, whole-share stocks, fractional crypto, no leveraged spot shorts, stop/target orders and risk halts. Use [market setup](docs/MARKETS.md) for demo and public/provider data commands. The [multi-market TradingView guide](docs/TRADINGVIEW.md) explains installation, costs and alerts.

Thirty additional candidate evaluations did not establish a reliable 70–80% strategy. Stock sample: 75% on only eight later-period trades; crypto default lost money. See [full results and limitations](docs/MULTI_MARKET_RESULTS.md). These strategies remain paper research.

### Grok methods and entry review

[Setup and measured results](docs/GROK.md): optional free `grok_consensus` research, with completed hourly/four-hour agreement and a structured Grok entry veto. The new method failed the profit/sample selection gates and is not enabled by default. No verified 70% win rate. Actual xAI calls require an explicit one-call CLI flag and your own key; no paid calls were made during development.

### Strategy lab and stronger paper controls

[Comparison, results and setup](docs/PRO_COMPARISON.md): ten-config chronological research, cost-aware band/MACD families, optional evidence-gated entries, durable cooldown/loss-streak guards, forex stop recovery during history failures, and persisted expectancy/equity monitoring. Tested against longer BTC history and existing ETH/EURUSD samples. No candidate met all selection gates; no verified 70% claim or automatic promotion.
# Latest video review and win-rate experiment

See [the video review](docs/VIDEO_REVIEW.md) for the checked public Grok desk, skeptical entry review, and the reproducible 16-profile RSI2 experiment. Reports explicitly distinguish observed historical wins from an unverified future probability.
