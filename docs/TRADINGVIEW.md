# Put BROBS on TradingView

Use `tradingview/BROBS.pine`. This is a Pine v6 port of the existing forex trend/momentum rules, with chart setups and simulated order-fill alerts. The rejected mean-reversion experiment is not enabled. It does not connect your Python dashboard or place broker orders.

1. Open TradingView, select **OANDA:EURUSD**, and choose the **1-hour** timeframe.
2. Open **Pine Editor**, create a new strategy, replace its contents with `tradingview/BROBS.pine`, and save it as **BROBS**.
3. Choose **Add to chart**, then open **Strategy Tester**. The script blocks entries on other currency pairs/timeframes.
4. In script settings, change the start/end dates for your test. Defaults cover the historical comparison window; **extend the end date for forward paper alerts**. Keep a later, fresh evaluation period separate from parameter selection.
5. Inspect closed-trade count, win rate, profit factor, net P/L and drawdown. Use Properties to match your feed's costs; default commission 0.0075% per fill approximates a 1.5-pip round-trip spread near EURUSD 1.0, and slippage is 5 minimum ticks per fill (0.5 pip on a five-decimal feed). These are approximations. Check your feed's minimum tick, spread, commissions and financing.
6. For notifications, create an alert, select **BROBS Forex Research**, choose **Order fills only**, and put `{{strategy.order.alert_message}}` in the Message field. Choose your app/email notifications and create the alert. Messages contain buy/sell/close, ticker, signal timestamp and `paper_only: true`.
7. Recreate alerts after changing code, inputs or chart context: TradingView runs the saved alert snapshot. Strategy fill notifications refer to TradingView's broker emulator. A setup triangle is a repeated qualifying setup, not confirmation of an executed trade.

No API keys or subscription purchase are needed to paste the strategy. Alert availability depends on your account's plan. **Pine has been reviewed against official v6 documentation but has not been compiled in TradingView here**; compilation and your feed's Strategy Tester results must be checked in your account. Python tests do not certify a Pine compilation.

## Differences from the Python engine

No future-looking data requests are used; decisions use confirmed bars and market entries fill on the next available tick (normally the next bar open). A stop/target bracket is submitted with each entry, using a tick distance derived from the signal close. Python brackets use actual entry price; gaps therefore differ. Pine uses the selected chart feed, approximate spread costs and its own intrabar fill assumptions; Python uses explicit bid/ask and stop-first ambiguous bars. Pine's intraday loss rule follows its session rather than the Python UTC anchor, and risk-rule halts do not have identical reset behavior. End-date liquidation occurs at the next available tick. Results should not be expected to match exactly. Bar Magnifier, if available, can improve intrabar detail but cannot prove live execution.

## Webhooks and the dashboard

TradingView can POST JSON to a public HTTPS webhook, with two-factor authentication required for webhook alerts. Its supported ports are 80/443. The current BROBS forex runner polls OANDA practice data independently; **no forex webhook adapter is deployed**. The older `brobs.alerts` localhost demonstration rejects forex and is not compatible with this Pine payload. Use app notifications now. Do not assume adding a webhook URL connects the strategy to BROBS or a broker.

Official references:
- https://www.tradingview.com/pine-script-docs/concepts/strategies/
- https://www.tradingview.com/pine-script-docs/concepts/alerts/
- https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/
