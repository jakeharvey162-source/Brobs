# BROBS broker automation (TradingView alert -> OANDA) — read before arming

## Read this first: what the evidence says

BROBS's own measured results (README, `docs/VALIDATION.md`, `docs/MULTI_MARKET_RESULTS.md`):

- EURUSD hourly holdout: **11 wins / 17 losses = 39.29% win rate on 28 trades**, +0.29% simulated return, one of three sub-periods lost money. Too few trades to claim an edge.
- Local ML veto: 50.74% direction accuracy vs a 53.38% majority baseline (no advantage).
- Thirty further candidate evaluations did **not** find a reliable 70–80% strategy. Crypto default lost money. The 75% stock figure came from eight trades.
- Public "75%–100% win rate" bots reviewed in `docs/HIGH_WINRATE_CANDIDATES.md` and `REAL_MONEY_READINESS.md` were not verified; one author's own forward account fell from 74.5% to 55.3% wins with a net loss.

**Win rate is not profit, and strategies are not additive** (blending a 39% and a 75% system does not make 80%). Nothing here — including the code below — creates an edge. Automation only makes a strategy's results arrive faster. If the strategy has no edge, real money simply pays spreads and swaps and loses. That is why the arming step below makes you type that sentence out.

**Recommendation:** run this on an OANDA *practice* account for a meaningful forward sample (hundreds of closed trades, several market regimes) and only consider real money if net expectancy after costs is clearly positive. Then start with an amount you can afford to lose entirely.

## What exists now (all fixture-tested; never run against a real broker)

| Piece | File | Purpose |
|---|---|---|
| Gateway | `brobs/live_orders.py` | Bracketed market FOK entries, durable journal, hard limits, `reconcile`, `flatten` |
| Webhook | `brobs/live_alerts.py` | Authenticated TradingView receiver, durable race-safe dedupe, broker-sourced quotes |
| Paper receiver | `brobs/alerts.py` | Unchanged paper-only gateway (a duplicate-execution race was fixed) |

**Safety rules enforced in code**

- Live is **disarmed**. It needs `BROBS_LIVE_ARM` set to the exact acknowledgement string (see `ARM_PHRASE` in `live_orders.py`), `OANDA_LIVE_TOKEN`/`OANDA_LIVE_ACCOUNT`, and `BROBS_LIVE_STOP_FILE`.
- Hard ceilings that configuration cannot exceed: ≤100,000 units/order, ≤20 orders/day, daily-loss limit ≤5% (defaults: 1,000 units, 3 orders, 2%).
- One position at a time: entries are refused unless the account has no open trades and no pending orders.
- USD-denominated, non-MT4 account required. Pairs: EUR_USD, GBP_USD, AUD_USD, NZD_USD only.
- Every entry carries a broker-side stop-loss and take-profit; the bracket is verified after the fill.
- The journal records "uncertain" **before** sending. A timeout never causes a resend, and blocks new entries until `reconcile` proves what happened.
- TradingView's price is only a sanity check (default ±0.3% of the broker mid). Execution uses fresh broker bid/ask.
- Duplicate events (retries, restarts, simultaneous deliveries) place exactly one order. Failed events are consumed, not replayed.

## Step 1 — practice account first

```powershell
$env:OANDA_PRACTICE_TOKEN   = "YOUR_PRACTICE_TOKEN"    # type on your own machine; never paste into chat or GitHub
$env:OANDA_PRACTICE_ACCOUNT = "YOUR_PRACTICE_ACCOUNT"
python -m brobs.broker_readiness --environment practice
$env:BROBS_ALERT_SECRET  = "a-long-random-secret-of-at-least-24-characters"
$env:BROBS_LIVE_CAPITAL  = "1000"        # the most capital BROBS may size against
python -m brobs.live_alerts              # prints environment=PRACTICE
```

## Step 2 — TradingView alert

Add `tradingview/BROBS.pine` to a forex chart (see `docs/TRADINGVIEW.md`), create an alert on **Order fills only**, enable *Webhook URL*, and use this message (one alert per pair, hard-code the pair):

```json
{"secret":"YOUR_SECRET","event_id":"{{ticker}}-{{timenow}}-{{strategy.order.action}}","symbol":"EUR_USD","market":"forex","action":"{{strategy.order.action}}","price":{{close}}}
```

TradingView can only post to a public HTTPS address on port 443, but the receiver listens on `127.0.0.1` only. Put a tunnel or reverse proxy (for example Cloudflare Tunnel) in front of `http://127.0.0.1:8768/alert`, keep that URL private, and never publish the secret. TradingView has historically limited webhook alerts to paid plans with two-factor authentication — check its current requirements.

## Step 3 — arming real money (only after Step 1 has a track record you trust)

```powershell
$env:OANDA_LIVE_TOKEN   = "YOUR_LIVE_TOKEN"
$env:OANDA_LIVE_ACCOUNT = "YOUR_LIVE_ACCOUNT"
python -m brobs.broker_readiness --environment live          # read-only checks
$env:BROBS_LIVE_STOP_FILE   = "C:\brobs\STOP"
$env:BROBS_LIVE_ENVIRONMENT = "live"
$env:BROBS_LIVE_CAPITAL     = "500"                          # a sum you can afford to lose
$env:BROBS_LIVE_ARM = "I ACCEPT THAT BROBS HAS NO PROVEN EDGE AND I MAY LOSE ALL FUNDS IN THIS ACCOUNT"
python -m brobs.live_alerts
```

Use a **dedicated** account and one BROBS process per account (one journal per account; the journal refuses to open for a different account). Do not run another bot on the same account.

## Stopping, recovering

```powershell
New-Item C:\brobs\STOP -ItemType File                        # block all NEW entries immediately
python -m brobs.live_orders flatten --environment live       # close every open trade, cancel pending orders
python -m brobs.live_orders reconcile --environment live     # resolve 'uncertain' attempts from broker truth
python -m brobs.live_orders status --environment live
Remove-Item C:\brobs\STOP                                    # only after review
```

`flatten` is risk-reducing, so it works even while the stop file exists and without arming. `reconcile` marks an attempt `not_found` only if the broker has no such order **and** 120 s have passed; a filled trade without confirmed stop/target stays blocking, and you must deal with it at the broker.

## Not done / not verified

- Never exercised against a real OANDA session; field names (`tradeOpenedID`, `@clientID` order lookup) follow OANDA's documentation but are untested live. Run it on practice first.
- Account eligibility, regional availability, USD-account requirement (a ZAR-denominated account is refused), lot/precision rules, spreads, swaps, news gaps and slippage are your responsibility to check; check legal/tax rules where you live.
- No continuous transaction-history reconciliation, partial-fill handling (FOK avoids partials), fee accounting, or news/calendar filter by default.
- Stops are broker-side, but a gap can fill beyond the stop price. Alerts can arrive late; the quote-sanity check limits but does not remove this.
- No independent security review. The receiver has a shared-secret check, size limit and localhost bind; a tunnel is your exposure.
