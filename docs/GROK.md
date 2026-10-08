# Grok methods and optional entry review

BROBS now has a free, deterministic `grok_consensus` research strategy and an optional structured Grok entry-review bridge. The deterministic strategy is **not the Grok model** and is not an approved replacement for the default: its measured results were worse. No xAI calls were made while building or testing this change. Real-money execution remains disabled.

## What informed this implementation

Reviewed source, rather than installing an exchange bot:

- [OpenLucky](https://github.com/MORNLONG/OpenLucky/tree/ca7e6c853c98e233322e6073788ddbf1479fa3a6), MIT: `okx_market.py` supplies technical indicators and multi-timeframe alignment; `ai_analyze.py` supplies typed/structured proposals and an error fallback. Its repository contains no reproducible profitability benchmark. Its leverage, OKX execution, self-assessed confidence and JSON repair are not imported.
- [HyperGrok](https://github.com/galleonlabs/hypergrok-trading-desk/tree/735e5c88697f5d381b919c20c9c882469527c024): separates market evidence, strategy, risk and review, with timestamped unavailable data and cost-aware risk sizing. This is an operating framework, not a demonstrated 70% trading strategy. No plugin or external agent instructions were installed.
- [Grok trading lab](https://github.com/zigley/grok-trading-lab-2026): inspected reports and repository structure. Simulation totals without the underlying reproducible code/data do not establish performance in BROBS.

BROBS implements common mathematical indicators independently. No third-party source code was copied. The ideas used are multi-timeframe agreement, explicit abstention on bad data, bounded structured review, and keeping risk/accounting outside the model. This improves the review architecture; it does not establish stronger prediction.

## Free strategy

```bash
python -m brobs.market_runner --market crypto --symbols BTC_USDT --strategy grok_consensus --db grok_crypto_research.db
python -m brobs.fx_runner --pairs EUR_USD --granularity H1 --strategy grok_consensus --db grok_fx_research.db
```

Crypto uses public Binance prices without a key; forex needs the existing OANDA practice credentials. Add `--demo --once` for synthetic smoke tests. Use separate databases for demo and real-price paper runs. The original `trend` strategy remains the default.

Rules: completed hourly OHLCV, hourly EMA50 aligned with EMA20 on **complete UTC-aligned four-hour buckets**, RSI2 recovering through 20 (inverse for forex shorts), ATR14/close no greater than 2%. Long exits at RSI2 >=70 or an hourly trend break; inverse for shorts. Stock and spot crypto cannot short. Missing bars, insufficient history and recent hourly gaps cause abstention. Because exchange sessions have gaps, this experimental variant can abstain extensively on stock data; the existing stock strategies remain available. It cannot use the old daily AAPL sample as hourly evidence. Stops, fees, risk budgets, pause and drawdown rules remain in the existing ledger.

EMA seeds use the first available close. Python research uses at most 500 previous bars. These exact research rules have not been added to or compiled in Pine: the existing TradingView script and its instructions remain at [TRADINGVIEW.md](TRADINGVIEW.md). TradingView cannot run this Python Grok API bridge.

## Optional Grok veto, with no automatic API spending

Start a runner with **both** file paths and one instrument:

```bash
python -m brobs.market_runner --market crypto --symbols BTC_USDT --db grok_review_paper.db --grok-request grok_request.json --grok-review grok_review.json
```

This example reviews the existing default strategy. Add `--strategy grok_consensus` only to research the rejected experimental method. For forex, the same two options work with `python -m brobs.fx_runner --pairs EUR_USD --db grok_review_fx.db`.

When a flat account gets an entry proposal, BROBS exports `grok_request.json`, containing the symbol, currency, signal ID, votes, last 100 completed bars, local paper equity and risk configuration. With no valid review it holds. If no setup exists, no request is generated. Exporting a request alone also blocks the entry. It does not create an approval.

For manual review, copy the request into your own Grok chat and ask it to use the included system instructions. Save its decision in `grok_review.json` with this exact envelope, replacing the example values:

```json
{
  "request_id": "copy the SHA256 request_id from grok_request.json",
  "created_at": "actual current UTC time, ISO8601",
  "decision": "veto",
  "reason": "Grok's actual supplied-evidence review",
  "model": "actual model used, or manual-review if unknown"
}
```

Allowed decisions are `approve` and `veto`. Never label a fabricated answer as a model response. Manual file reviews are trusted local inputs, not cryptographically authenticated xAI responses; anyone able to edit the file can approve. Keep them private.

If you already have an xAI API account and deliberately want **one billed call**, put `XAI_API_KEY` in your local environment, choose an available structured-output Grok model, and run:

```bash
python -m brobs.grok_review --request grok_request.json --output grok_review.json --model YOUR_AVAILABLE_GROK_MODEL --api
```

Replace the model placeholder with its actual `grok-...` identifier. The command does not call the API unless `--api` is explicit. It uses the [official structured-output contract](https://docs.x.ai/developers/model-capabilities/text/structured-outputs) at `https://api.x.ai/v1/chat/completions`, one request, 500 output tokens maximum, 30-second timeout, no tools, no search, no automatic retries and no order endpoint. The selected model may impose its own costs. No model is assumed free. No live xAI connection was verified here: transport/schema/error handling were tested with fixtures.

On the next fresh-price tick, an approval must match the exact SHA256 evidence and be at most 15 minutes old, with no future date. Changed bars, strategy, source or account evidence require a new review. Missing, malformed, stale, mismatched or extra fields block entry. The same bar can enter once after a pending review; repeated approvals do not duplicate entries. Reason/model are displayed in the existing dashboard vote history. They are explanations, **not calibrated win probabilities**.

The review cannot create an entry without a strategy proposal, reverse its side, supply quantity/leverage, loosen a stop, change risk limits, block a strategy close or suppress fresh-quote stops. Stops require a connected running runner. Account risk checks run after any approval. No news/social/funding tools are connected; the model is explicitly told those facts are unavailable.

## Measured result: 70% not achieved

Six variants per dataset were declared: RSI recovery thresholds 10/20/30, each with default/half-default stop, reward:risk 2. Only the first 70% of bars was used for selection; its final 40% was validation. Eligibility required 30+ closed validation trades, positive P/L and profit factor >=1.2. **None passed on any of the three datasets.** The fixed threshold20/default-stop version is nevertheless reported on the final 30% so failures are visible.

| Dataset, later test | New method trades | Wins/losses | Win rate | New method return | Default return |
|---|---:|---:|---:|---:|---:|
| BTC/USDT, July–September 2026 | 60 | 9 / 51 | 15.00% | -4.3037% | -1.2204% |
| ETH/USDT, July–September 2026 | 73 | 16 / 57 | 21.92% | -5.0770% | -0.4582% |
| EUR/USD, August–September 2026 | 41 | 16 / 25 | 39.02% | -0.3889% | +0.2810% |

Returns include fees, spread and slippage. Doubling spread/slippage and adding commission makes all three worse. All samples have fewer than 100 closed trades. ETH was new to this strategy search; BTC and EUR/USD had already been inspected in earlier work. This is deterministic method research, **not a backtest of actual historical Grok answers**. Swaps, dividends, depth, partial fills and outages are not modeled. There is no valid 70% claim or evidence to promote this variant.

Full reports: `research/grok-btc-evaluation.json`, `research/grok-eth-evaluation.json`, `research/grok-forex-evaluation.json`. ETH provenance includes checksums for the official public archives; raw crypto prices are downloaded locally, not redistributed.

Reproduce ETH:

```bash
python -m brobs.public_data --symbol ETHUSDT --months 2026-01 2026-02 2026-03 2026-04 2026-05 2026-06 2026-07 2026-08 2026-09 --output local-data/ETHUSDT_1h.csv
python -m brobs.grok_research --csv local-data/ETHUSDT_1h.csv --market crypto --symbol ETH_USDT --output local-data/grok-eth-evaluation.json
python -m unittest discover -s tests -v
```

Use `BTCUSDT`/`BTC_USDT` for the BTC report; EUR/USD uses the committed `research/data/EURUSD_1h.csv`. Thresholds and stop variants were not changed after observing the ETH later test. New forward paper evidence is needed for further strategy decisions.
