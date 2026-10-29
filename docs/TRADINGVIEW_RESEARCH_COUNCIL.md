# BROBS Research Council: TradingView read-only indicator

This is a **research-only chart display**. It does not trade, send alerts, connect a broker, receive deposits, or know the Python AI agents' conclusions. It is intentionally separate from tradingview/BROBS.pine, which remains an independently implemented paper strategy.

## Purpose

The existing BROBS Python project has research agents, paper-account state, and historical analysis. TradingView Pine Script cannot execute that Python code or host the AI-provider APIs as if they were Pine functions. This small indicator instead shows *independent, deterministic chart observations*:

- **Trend observer:** compares fast/slow moving averages and a long-term average.
- **Momentum observer:** categorizes RSI as positive, negative, or balanced.
- **Volatility observer:** identifies bar-return volatility above a user-chosen threshold. This threshold is for display, not a proven profit filter. It must be reconsidered for different timeframes and assets.
- **Data observer:** flags insufficient history and invalid settings.
- **Council summary:** reports alignment, disagreement, or a reason to withhold a conclusion.

These are simple statistical rules, **not multiple LLM employees or an 81% prediction engine**. They do not generate BUY/SELL orders, alerts, strategy entries, or an expected win probability. Agreement between observations is not independent corroboration.

## View on TradingView charts (no brokerage account needed)

1. Open the Pine Editor on any TradingView chart.
2. Create a new **indicator** script.
3. Replace the template with the contents of tradingview/BROBS_COUNCIL.pine.
4. Save it under any name and select **Add to chart**.
5. Observe the research table at the top-right and optional moving-average lines. Use ordinary candles and compare different symbols/timeframes as an educational exercise.

The same indicator can *display chart observations* on forex, shares, crypto, and Bitcoin symbols, but it makes no market-wide portfolio decisions. Each chart is separate. Elevated volatility is measured as the standard deviation of percent price changes *per chart bar*: a 1-minute reading and a daily reading are not interchangeable.

## What remains outside TradingView

- BROBS's Python research, news provenance checks, model-review process, simulations, and SQLite records stay outside Pine.
- Any genuine multi-model experimental council would need an external research environment and rigorous evaluation. This indicator deliberately does not claim to receive that council's decisions.
- Pine scripts are limited by TradingView's language, data access, and runtime quotas.
- TradingView's brokerage connections are distinct from its chart indicators and strategy emulator.

## Evaluation before calling anything better

Keep the existing reported sample (11 wins in 28 closed historical trades) as an evidence baseline, **not a target to rewrite**. An apparent 20 or 25 wins out of 28 could be a tiny selected sample, hindsight optimization, or a strategy with outsized losses. Meaningful assessment uses unseen chronological periods, several market regimes, realistic trading costs, per-trade P&L, drawdown, total number of observations, and reproducible comparisons with simple baselines. A statistical interval from 28 trades is too wide to establish a stable future win probability.

There is **no proven path from this indicator to any promised win rate**. It does not place real or simulated orders and must not be portrayed as an automated money-making app.

## Testing limitations

Automated repository tests verify that this Pine file remains a read-only indicator without trade/order/alert instructions, and that the education-only labels are present. Those are static checks only. **Pine compilation and chart rendering have not been validated inside TradingView**. A user must verify the displayed code using Pine Editor before relying on any visual interpretation.

Official TradingView docs:
- https://www.tradingview.com/pine-script-docs/writing/limitations/
- https://www.tradingview.com/support/solutions/43000756695-how-to-trade-on-tradingview/
- https://www.tradingview.com/pine-script-docs/faq/strategies/
