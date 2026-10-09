# Execution status and engine comparison

BROBS is not currently one of the best demonstrated profitable trading systems. Its public reports do not establish a 70% win probability. A functioning execution engine and a profitable strategy are separate achievements.

| Capability | BROBS | Established engines |
| --- | --- | --- |
| Automated signals, sizing, local entries/exits | Implemented in Python polling runners | Freqtrade and LEAN provide this with larger ecosystems |
| Restart-safe local account and monitoring | SQLite ledger, loopback dashboard, paper protections | Larger monitoring/deployment and reconciliation systems |
| Real broker execution | Not activated | Freqtrade exchange integrations; LEAN brokerage integrations |
| OANDA practice order entry | New separately tested gateway; not wired into polling runner | Brokerage integrations are mature components in established engines |
| Broker-side stop/target | New gateway creates both with FOK entry | Established engines support broker/exchange-dependent protection |
| Broker transaction reconciliation and full trade lifecycle | Still missing; do not present local simulated fills as broker fills | More extensive reconciliation, order states and restart handling |
| Verified profitable strategy | No; current historical candidates fail acceptance | Engine functionality does not certify any particular strategy's profit |

Sources: [Freqtrade backtesting](https://www.freqtrade.io/en/stable/backtesting/), [Freqtrade strategy modes](https://www.freqtrade.io/en/stable/strategy-customization/), [QuantConnect LEAN](https://github.com/QuantConnect/Lean), [OANDA endpoints](https://developer.oanda.com/rest-live-v20/development-guide/), [OANDA order creation](https://developer.oanda.com/rest-live-v20/order-ep/).

## What repositories were actually used

Backtrader 1.9.78.123 was installed and executed as an independent research reference. Freqtrade's public Bollinger/RSI example and protection documentation were examined; BROBS's strategies/protections were independently implemented, not copied engine code. OpenLucky, hypergrok-trading-desk and zostaff/grok-trading-desk informed reviews of multi-timeframe signals and skeptical vetoes. No audited profitable history for these Grok projects was established. They were not installed as operational BROBS bots. Adding their prompts or naming several roles does not transfer a proven trading edge. See `docs/GROK.md`, `docs/VIDEO_REVIEW.md`, and `docs/PRO_COMPARISON.md` for pinned sources and actual results.

## New practice gateway

`brobs.practice_orders.entry_plan` builds USD-quoted forex market-entry requests from fresh executable quotes and capped paper capital. It rounds currency units down, caps full notional, includes a price bound, uses FOK/OPEN_ONLY and supplies broker-side stop-loss/take-profit. No leverage-based position sizing is used. It does not permit arbitrary raw order payloads.

`PracticeOrders.submit` uses only `api-fxpractice.oanda.com`. It validates the broker's USD account, rejects existing trades/pending orders and MT4 accounts, rebuilds the order against current prices, and binds its SQLite journal to the account. A signal-derived client identifier and a committed pre-send uncertainty record prevent blind retries after a crash/timeout. Filled, cancelled and rejected responses are distinguished. An unknown response or timeout blocks subsequent submissions until an operator investigates the broker. HTTP redirects are refused to protect credentials and the endpoint boundary.

After an entry fill, the gateway reads the broker trade and checks both protective orders are pending (or that the trade is already closed). Missing protection blocks further entries. A failed confirmation request preserves the uncertainty halt.

Only fixture transports were used in development: no broker order, practice or live, was sent. An end-to-end credentialed broker session is not verified. This module is a separately callable entry gateway, not a completed automatic broker runner. The local dashboard does not show its broker account. It does not reconcile transaction history, implement daily broker-account drawdown halts, close existing broker trades on strategy exits, supervise a service or recover uncertainty automatically. Do not bypass the unknown-status journal by deleting the database.

The existing `fx_runner` remains automatic local paper execution with practice market data. `market_runner` remains automatic local stock/crypto paper execution. Polling continues only while its process is running. Grok review is optional and requires a supplied review; verified live news/sentiment is unavailable. TradingView supplies a separate Pine simulation/notifications, not automatic deployment of Python bots. Installation steps are in `docs/TRADINGVIEW.md`.

Real-money trading has not been switched on. The missing broker lifecycle and failed strategy validation remain material gaps; no future earnings estimate is supplied.
