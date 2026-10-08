# Forex practice-data integration

**Important:** OANDA practice account provides real broker-hosted forex candles and account summaries, but BROBS does **not** submit OANDA orders. All executions are simulated in BROBS's local paper ledger. This is NOT broker-connected paper order execution.

OANDA practice API eligibility varies by jurisdiction and account. Create a compatible practice account and token at OANDA if eligible. Do not paste credentials in chat or commit them to GitHub.

Set environment variables in your shell:

- `OANDA_PRACTICE_TOKEN`: personal practice API token
- `OANDA_PRACTICE_ACCOUNT`: practice account ID

Then:

```bash
python -m brobs.forex_runner --pair EUR_USD --db brobs_paper.db
python -m unittest discover -s tests -v
```

The runner fetches 200 completed H1 midpoint candles from the OANDA practice host, evaluates the five research agents, simulates any eligible trade locally, and saves portfolio state and decisions in SQLite. Run it manually for now; no unattended scheduler is configured. Repeated processing of the same candle is skipped within the last 100 logged events. SQLite event + snapshot writes are transactional, but simultaneous runners and interruption between simulation and persistence need further hardening. The simulated accounting is generic and does not correctly model all FX currency conversions, margin, spreads or rollover charges; its returns must NOT be treated as realistic FX results.

A production broker-paper integration needs the official OANDA practice order endpoint, exact instrument rules, fill reconciliation, margin and account-currency conversion, broker order IDs, idempotency, and safeguards. No live hostname or real-money order function is included.
