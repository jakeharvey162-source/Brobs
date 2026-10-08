# Forex, stock and crypto paper accounts

BROBS uses separate durable local ledgers. It never sends orders to a broker or exchange. Forex supports the existing USD-quoted pairs; stocks use USD and whole shares; crypto uses **USDT**, fractional units down to 0.000001, and long-only spot simulation. A stock/crypto sell closes a long position; it cannot open a borrowed short. Every open position reserves its full notional value, with a 20% equity cap per symbol and no leverage. Fees, bid/ask, slippage, stop/target, daily loss, drawdown halts, duplicate events, persistence and quote freshness use the same accounting layer.

| Market | Supported instruments | Data | Default stop / target |
|---|---|---|---|
| Forex | EUR_USD, GBP_USD, AUD_USD, NZD_USD | Eligible OANDA practice account | 0.5% / 1% |
| Stock | AAPL, MSFT, NVDA, SPY | Eligible Alpaca paper credentials, IEX data | 2% / 4% |
| Crypto | BTC_USDT, ETH_USDT | Binance public data API; no credentials | 2% / 4% |

Accounts remain separate. Displayed balance is initial capital plus realized P/L less paid entry fees; reserved notional/free margin explain the collateral commitment. This is a simulator, not a brokerage cash/settlement statement. There is no USD/USDT conversion, combined cross-account risk, stock corporate-action processing, dividend credit, broker cash reconciliation or leveraged futures support.

## Start a demo on Windows

Install Python 3.11+ with **Add Python to PATH** selected. Download the existing BROBS repository ZIP, extract it, open PowerShell in the folder containing README.md and the `brobs` folder. If `python` is unavailable, use `py -3` in its place.

Crypto demo, first terminal:

```powershell
python -m brobs.market_runner --market crypto --symbols BTC_USDT ETH_USDT --demo --db brobs_crypto.db
```

Second terminal:

```powershell
python -m brobs.app --market crypto --db brobs_crypto.db --port 8768
```

Open http://127.0.0.1:8768. Synthetic results are labeled and cannot establish a win rate. Use a separate database for real data (for example `crypto_public.db`), so synthetic and historical/live performance cannot be mixed.

Stock demo:

```powershell
python -m brobs.market_runner --market stock --symbols AAPL MSFT --demo --db stock_demo.db
python -m brobs.app --market stock --db stock_demo.db --port 8769
```

Run these in separate terminals. Forex remains `python -m brobs.fx_runner` plus `python -m brobs.app --db brobs_fx.db --port 8767` after local OANDA practice credentials are set. Use a separate port for each dashboard.

## Current market data

Crypto needs no key:

```powershell
python -m brobs.market_runner --market crypto --symbols BTC_USDT ETH_USDT --db crypto_public.db
python -m brobs.app --market crypto --db crypto_public.db --port 8768
```

Binance access is subject to availability and regional restrictions; this app cannot bypass them. REST bookTicker has no native event timestamp, so BROBS uses exchange server time fetched before the bid/ask snapshot. HTTP caching, network delays and missing quotes can block the runner. This is weaker freshness evidence than a timestamped exchange stream. Stale/invalid data cannot open positions. The runner must stay connected/running to evaluate paper stops.

Stocks require your own eligible Alpaca paper account/data credentials, entered only locally:

```powershell
$env:ALPACA_PAPER_KEY = "YOUR_PAPER_KEY"
$env:ALPACA_PAPER_SECRET = "YOUR_PAPER_SECRET"
python -m brobs.market_runner --market stock --symbols AAPL MSFT --db stocks_iex.db
python -m brobs.app --market stock --db stocks_iex.db --port 8769
```

The stock client only GETs clock, hourly bars and latest quotes. It uses the IEX feed, which is not the entire US market/NBBO. Fresh quotes with positive bid/ask sizes are required. Closed exchange sessions do not create new entries; overnight positions and gaps remain possible. Completed recent hourly history is required for entries. A missing/stale history blocks entries but **fresh-quote stop processing continues**. Credentialed stock data was fixture-tested, not verified against a user's account. No new account or paid service is created by BROBS.

## Strategies and pause

The default is `trend`. Experimental alternatives are `rsi_pullback`, `rsi2_reversion`, and `donchian`, for example:

```powershell
python -m brobs.market_runner --market crypto --strategy rsi2_reversion --db crypto_rsi_experiment.db
python -m brobs.market_runner --market crypto --pause --db crypto_rsi_experiment.db
python -m brobs.market_runner --market crypto --resume --db crypto_rsi_experiment.db
```

Keep the runner active after pausing so it can evaluate stops. Switching strategy should use a fresh experiment database. These alternatives have not demonstrated the target win rate and are not promoted automatically. Stock/crypto default fees/slippage are in `market_book.default_config`; market research can evaluate alternate stops/targets without changing a running account. `brobs.fx_runner` retains its existing forex rules, including its latest input guards.

## Reproduce crypto research

```powershell
python -m brobs.public_data --symbol BTCUSDT --months 2026-01 2026-02 2026-03 2026-04 2026-05 2026-06 2026-07 2026-08 2026-09 --output research/data/BTCUSDT_1h.csv
python -m brobs.market_research --csv research/data/BTCUSDT_1h.csv --market crypto --symbol BTC_USDT --output research/crypto-strategy-evaluation.json
python -m unittest discover -s tests -v
```

The archive downloader verifies SHA-256 and requires ordered, contiguous hourly data. It does not fill missing candles synthetically. Date selection/fees/strategy changes alter results. Never tune repeatedly on the same final period and present it as unseen evidence. See the win-rate report and TradingView guide for results/limitations.
