# TradingView integration (paper-only)

TradingView alerts can POST JSON to a publicly reachable HTTPS webhook endpoint. BROBS includes a **localhost-only** example receiver, so it is **not directly reachable by TradingView**. Use a trusted HTTPS reverse proxy or hosted receiver with authentication, durable event storage, and rate limits before accepting remote alerts. Do not expose a development server publicly.

Start locally: set a long random `BROBS_ALERT_SECRET` environment variable, then `python -m brobs.alerts`.

Example TradingView alert body (replace secret with your own; never commit it):

```json
{"secret":"YOUR_RANDOM_SECRET_AT_LEAST_24_CHARS","event_id":"{{ticker}}-{{time}}-{{close}}","symbol":"{{ticker}}","market":"crypto","action":"buy","price":"{{close}}"}
```

Create an alert in TradingView from a chosen Pine Script strategy or indicator. Configure webhook URL pointing to your secured HTTPS gateway at `/alert`, then paste the JSON alert body. Check TradingView's plan eligibility and current webhook rules. Some alerts are limited by subscription; do not rely on the service for guaranteed execution. Avoid putting brokerage keys in alert messages.

IMPORTANT: This demo gateway uses in-memory portfolio state and deduplication; restarts lose both. It uses alert prices instead of broker-verified quotes. **Never connect this gateway to real money.** A production adapter needs durable idempotency, signature/authentication, secure secrets, risk enforcement, order reconciliation, position persistence, event age validation, market session handling and actual broker paper-account testing.

## Forex update

The old gateway now rejects `market: forex`: an alert's midpoint is not a fresh executable bid/ask. The new persistent FX runner operates independently from TradingView. A forex gateway would need to authenticate and persist signals, then obtain fresh broker quotes and pass the same FX risk controls; that integration has not been supplied or publicly deployed.
