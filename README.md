# BROBS AI

Autonomous multi-market trading research platform. **Paper trading only. No guaranteed returns.**

## Markets
Crypto, forex, and stocks are supported as typed instruments in the common strategy/risk engine. Broker APIs, live data providers, and live order execution are **not connected**. Historical candle CSVs or other adapters must supply actual prices.

## Quick start

```bash
python -m unittest discover -s tests -v
python -m brobs.demo
```

The demo uses **synthetic data** and generates simulated trade decisions; its results are not investment performance. No dependencies or API keys are required for these commands.

## Architecture
- `brobs/models.py`: market instruments, candle bars, actions, orders and portfolio state.
- `brobs/strategy.py`: example moving-average crossover signals (educational, not profitable by default).
- `brobs/risk.py`: position sizing, stop placement and circuit breakers.
- `brobs/paper.py`: paper-only market execution with spread/fee/slippage simulation.
- `brobs/demo.py`: reproducible illustrative walk-through.

## Live execution safety
No live broker implementation is shipped. Do not provide credentials or transfer money to this project. Live trading requires separate authorized brokerage integration, secure secrets storage, eligibility checks, accurate pricing, extensive forward testing, order reconciliation, kill switches and manual activation. Daily stop rules cannot guarantee maximum realized loss under gaps or failures.

## Third-party foundations to evaluate
[QuantConnect LEAN](https://github.com/QuantConnect/Lean) for multi-asset execution/backtesting; [Freqtrade](https://github.com/freqtrade/freqtrade) for crypto research; [Microsoft Qlib](https://github.com/microsoft/qlib) for quantitative ML research. These are references, not vendored dependencies. Check licenses and verify their claims before integration.
