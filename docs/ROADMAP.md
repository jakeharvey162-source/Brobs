# BROBS readiness

A tested local forex-paper app is now implemented. An arbitrary percentage is not evidence of trading readiness.

Completed: validated market-data adapter, USD-only FX accounting, durable atomic portfolio/events, polling, loss controls, dashboard, chronological historical replay, win/loss statistics, cost stress, optional Backtrader reference and local sklearn research agent.

Remaining before broker-connected order readiness:

1. Validate a credentialed practice-data session, including weekends, stale quotes and disconnections.
2. Add **practice broker order** submission/reconciliation if requested; it is deliberately absent today.
3. Model swaps, exact broker instrument specifications, liquidity/partial fills and all supported account conversions.
4. Run sustained forward-paper testing across several pairs and market regimes. Current evidence has only 28 holdout trades on one pair.
5. Add deployment authentication, monitoring, encrypted secret management, maintenance procedures and independent security review before public hosting.

Real-money execution stays disabled. Historical returns do not establish future profits. Existing stock/crypto research remains available but is not broker-integrated.
