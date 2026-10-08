# BROBS multi-agent research architecture

Five deterministic agents run without API keys:

1. **Trend**: SMA crossover research vote.
2. **Momentum**: two-window directional research vote.
3. **Volatility**: abnormal historical-return volatility veto.
4. **Information**: checks for verified timestamped news input; never fabricates news or sentiment.
5. **Risk**: equity circuit breaker veto.

**Coordinator** requires both directional agents to agree and both veto agents to permit action. Information without an actual feed abstains. This is a research-only voting prototype; it is not connected to any broker, scheduler, portfolio ledger or historical backtester. Voting does not demonstrate predictive skill or profitability.

## Candidate open-source engines (not yet integrated)
- QuantConnect LEAN (Apache-2.0): multi-asset engine, best candidate for core execution and robust backtests.
- Hummingbot (Apache-2.0): crypto market making and connectors, optional dedicated subsystem.
- Freqtrade (GPL-3.0): crypto research/dry-run; license obligations must be assessed before reusing source.
- Qlib (MIT): ML quantitative research, separate from execution.

Do not run multiple order-execution frameworks against the same account without centralized order ownership and reconciled exposure. Next milestones: broker sandbox adapter, accurate calendars/instrument specs, durable event log, monitored runner, real historical walk-forward evaluation, production-grade security review. **Real-money orders are disabled.**

## Current implementation update

The original coordinator above is preserved. The new forex runner uses `fx_signals.py` with forex-scale trend, momentum and volatility votes, then the `fx.py` risk/accounting layer. `ml_agent.py` provides an optional local sklearn veto with an internal chronological validation gate. `fx_runner.py` polls practice-market data; `app.py` reads the durable FX ledger. These are executable components, not external autonomous agents. No verified news/calendar feed or broker-order execution exists.
