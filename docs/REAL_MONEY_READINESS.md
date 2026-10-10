# BROBS real-money connection readiness — no missing pieces hidden

## Free versus funded

The execution **software** can be free and open source. The trading account, capital, spreads, commissions, exchange minimum order size, country eligibility and exchange risk are not guaranteed free. No repository can supply a legal broker account belonging to someone else or an audit of a profitable strategy.

**OANDA v20** publicly documents free-to-access APIs for eligible account holders:
- **Practice** REST host: `api-fxpractice.oanda.com`
- **Live** REST host: `api-fxtrade.oanda.com`
- Both require an eligible OANDA account and owner-created API token
- Real orders: `POST /v3/accounts/{accountID}/orders`
- Read-only account check: `GET /v3/accounts/{accountID}/summary`
- Read-only broker positions: `GET /v3/accounts/{accountID}/openTrades`
- Read-only pending orders: `GET /v3/accounts/{accountID}/pendingOrders`

**What BROBS has now:** a tested forex paper ledger, TradingView Pine research script (Pine compilation in the TradingView UI not independently verified), an OANDA **practice** order-entry module using market fills + attached broker stop-loss/take-profit, a durable pre-send journal, and a new read-only practice/**live** account preflight. The practice entry module remains separately callable and is **not** connected to the automated forex polling runner; it has not sent a credentialed test order on an actual practice account.

The read-only preflight is a foundation for onboarding: it checks USD denomination, account liquidity, open positions and pending orders, conflicting account state, and optionally unknown/unsafe entries in the local journal. **It never calls order creation**, even in live mode. Passing preflight does not enable live trading or establish safe operation.

## Run the no-order broker preflight

Keep keys on **your own machine**, never in GitHub, Vercel browser variables, a TradingView alert, or chat. Obtain them yourself in OANDA's account management portal if you are eligible.

Windows PowerShell — practice:

```powershell
$env:OANDA_PRACTICE_TOKEN = "PASTE_ON_YOUR_OWN_DEVICE"
$env:OANDA_PRACTICE_ACCOUNT = "YOUR_PRACTICE_ACCOUNT_ID"
python -m brobs.broker_readiness --environment practice
```

Windows PowerShell — live, **read only**:

```powershell
$env:OANDA_LIVE_TOKEN = "PASTE_ON_YOUR_OWN_DEVICE"
$env:OANDA_LIVE_ACCOUNT = "YOUR_LIVE_ACCOUNT_ID"
python -m brobs.broker_readiness --environment live
```

Your live account must actually support OANDA v20. Regional access restrictions may apply. The script prints only sanitized audit output, not credentials or upstream response text. This preflight requires internet access and your own valid tokens; its HTTP connectivity could not be tested with credentials in CI, so automated tests use simulated transport objects.

Optional practice order journal check:

```powershell
python -m brobs.broker_readiness --environment practice --journal practice_orders.db
```

Do **not** delete an unresolved journal entry to clear an unsafe broker state; reconcile it against the broker first.

## What remains before *automated* live-money execution can be called ready

1. Validate OANDA account eligibility, its instrument, lot and margin/precision rules.
2. Run an actual consented practice broker order with verified stop and profit orders; no broker credentials were supplied for this step.
3. Implement and test continuously reconciling broker position/order/transaction history, including partial fills, rejections, fees, restarts and network timeouts; never treat an HTTP timeout as an unfilled order.
4. Implement broker-side exit operations with exactly-once semantics or manual recovery; verify that stop-loss and risk halts work under failure conditions.
5. Prevent competing runners from managing the same account; ensure funds cannot be overcommitted, with a human-operated emergency stop and least-privilege credentials.
6. Replay multiple genuinely unseen datasets with realistic costs, then forward-paper a representative sample to establish positive risk-adjusted expectancy; BROBS's current historical strategy candidates fail acceptance.
7. Complete independent operation/security review and verify legal/tax requirements in the user's location, then request a **separate explicit live-risk approval** from the account owner.

These are engineering and real-world verification gaps, **not** a flag to bypass. BROBS will not auto-enable real-money trading just because a third-party project claims a 75% win rate.

## Other free frameworks and repos reviewed

- **Freqtrade** (https://github.com/freqtrade/freqtrade): GPL open-source crypto trading engine with supported exchanges, backtests and dry-run; BROBS has a separate pinned Freqtrade integration and tested offline reference. It is not the same broker/ledger as BROBS. Its own live setup needs venue access, user-managed keys and risk controls.
- **OANDA REST v20** (https://developer.oanda.com/rest-live-v20/development-guide/): direct official HTTP interface; avoids a third-party Python wrapper. A free open-source wrapper, `oandapyV20`, exists, but it does not eliminate broker credentials or prove fills.
- **CCXT** (https://github.com/ccxt/ccxt): broad exchange API library, but exchange permissions, markets and API credentials vary.
- **LEAN** (https://github.com/QuantConnect/Lean): full research/execution stack but not itself a profitable strategy.

## 75%+ strategy claims and why none has been promoted

- `zevrichards/freqtrade-strategies` reports **74.5% historical wins on 314 crypto trades**. The author's later report also shows **55.3% wins and a loss across 85 trades**. No declared LICENSE at time of review; source not redistributed.
- `aashir-athar/MiND-Shot` reports a **78.4% in-sample** ETH leveraged futures strategy and **75.9%** on another setup; no declared LICENSE at time of review, and neither score establishes unseen profitable execution. Not copied.
- `jozef-pridavok/binstra` reports **100% wins in its BTC backtest**, but win rates on a dip-buying/basket strategy can conceal open losers and tail risk. Source is MIT-licensed Rust with an independent runtime, **not Python forex/spot broker API compatible**. Not passed BROBS's performance gates.
- `AbdulMomen2/golden-cross-trading-bot` reports **75% from only four AAPL trades**, with no fees or slippage included. No declared LICENSE; not valid evidence for BROBS or compatible automatic execution.
- `darkvolg/trendrider-strategy` (MIT): already copied into BROBS at `integrations/freqtrade/TrendRiderStrategy.py` with copyright notice. It requires a separate Freqtrade runtime and is not an independently validated 70% winner.

**Win rate is not additive.** Combining 39% and 75% strategies does not yield 80% or 90%; it may worsen fees, trade overlap and drawdown. Selection should be based on independent, comparable, held-out net profit, number of trades, costs and drawdown, and should have a robust "no trade" option.

## Reproducible test coverage

`python -m unittest discover -s tests -v` includes mocked environment separation, read-only broker methods, count consistency, invalid account/currency and unresolved journal cases. CI also builds/tests earlier paper-trading behavior. **No real funded account or real broker order was involved**.

Official sources:
- OANDA API: https://developer.oanda.com/rest-live-v20/development-guide/
- OANDA order endpoint: https://developer.oanda.com/rest-live-v20/order-ep/
- Freqtrade dry-run: https://www.freqtrade.io/en/stable/configuration/
