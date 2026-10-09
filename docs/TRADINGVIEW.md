# Install BROBS on TradingView — step by step

The file is **tradingview/BROBS.pine** in the existing BROBS repository. It is a Pine v6 strategy for chart signals, strategy testing and paper order-fill notifications across forex, stocks and crypto. It is not a copy of the Python application, and it does not execute broker orders or connect the Python dashboard to TradingView.

## 1. Get the code

1. Open https://github.com/jakeharvey162-source/Brobs.
2. Open the **tradingview** folder, then **BROBS.pine**. Click **Raw** and copy the entire script, starting with `//@version=6`.
3. Alternatively choose **Code → Download ZIP**, extract it, open `tradingview/BROBS.pine` in Notepad, press Ctrl+A then Ctrl+C. Do not paste README text or the entire ZIP into Pine Editor.

## 2. Open a chart

Sign in at https://www.tradingview.com/ and open a chart. Search for the symbol and choose its exchange/provider deliberately:

| Market | Example chart | Initial timeframe | Simulation direction |
|---|---|---|---|
| Forex | OANDA:EURUSD, OANDA:GBPUSD | 1 hour | Long and short, USD-quoted forex |
| Stocks | NASDAQ:AAPL, NASDAQ:MSFT | 1 hour | Long only; sell closes the long |
| Crypto | BINANCE:BTCUSDT, BINANCE:ETHUSDT | 1 hour | Long-only spot, USDT quote |

Use normal candles. Heikin Ashi, Renko and other synthetic bars can give unrealistic fills. The stock research sample is **daily** AAPL from 2015–2017; it does not validate today's hourly AAPL strategy. The latest crypto research uses hourly BTCUSDT. Other markets/timeframes remain unvalidated experiments.

## 3. Install the strategy

1. Open **Pine Editor** (its position may vary with TradingView's layout).
2. Choose **Open → Templates → New strategy** (some layouts show Create new).
3. Select all template code and replace it with the copied BROBS script.
4. Save it as **BROBS**.
5. Click **Add to chart**. The displayed strategy name is **BROBS Multi-Market Paper**.
6. If TradingView shows a compile error, record its exact message and line. **This script has been reviewed against official Pine v6 documentation but has not been compiled in TradingView here. Python tests do not verify a Pine compilation.**

The chart shows teal/orange averages and buy/sell setup triangles. A triangle is a qualifying setup, not proof of a fill. Order markers and the Strategy Report/Strategy Tester show emulator trades. A red setup on stocks/crypto can represent an exit; it does not permit a borrowed short.

## 4. Set dates, costs and risk

Open the strategy's gear icon:

- **Inputs:** start with **Trend momentum**, automatic market stop, 0.5% risk budget, 20% maximum notional, 2:1 target/stop. Automatic stop is 0.5% for forex and 2% for stocks/crypto. The risk budget is a cap; the no-leverage notional cap can make actual risk smaller.
- **Dates:** defaults are January 2026 through January 2030, so forward paper signals are enabled. For historical comparisons, set a fixed range. For the old stock sample, use 2015–2017 and a daily chart. Keep future evaluation dates separate from strategy selection.
- **Properties:** initial paper capital is 10,000 **in the chart's quote currency**. A BTCUSDT chart is a USDT simulation, not a USD account. Each chart/strategy is a separate account; no multi-symbol portfolio risk is enforced across charts.
- **Costs:** the default commission is **0.1% each fill**, suitable only as a crypto fee example. It is not appropriate for every market. Configure your actual provider's fees/spread/slippage. For forex, 0.0075% per fill is only an approximate spread-cost example near EURUSD 1.0; it is not a verified broker fee. For stocks, use applicable commission and spread costs.
- **Slippage:** TradingView's value is **minimum ticks**, not pips or percent. Five ticks means 0.5 pip on a five-decimal forex feed, $0.05 on a stock with $0.01 ticks, and only $0.05 on BTC if its tick is $0.01. To approximate Python's 0.05% crypto slippage at BTC=80,000 with tick=$0.01, use about **4,000 ticks**, then reassess when prices change. Constant ticks cannot exactly match percent slippage over a long history.

Experimental RSI pullback, RSI2 reversion and Donchian breakout modes are available for comparison. Their presence does not mean they passed the profit/sample checks. Do not reduce costs, widen losing stops or change dates just to obtain a 70–80% headline.

## 5. Read Strategy Tester / Strategy Report

Open the strategy report. Inspect total closed trades, percentage profitable, net P/L, profit factor, maximum drawdown, average winning and losing trade, and the trade list. Win rate is winning closed trades divided by all closed trades. A 75% win rate from eight trades is not comparable to a well-tested 75% strategy with thousands of independent trades.

Check several periods, include losing market conditions, and reserve a later period for evaluation. Compare against cash/buy-and-hold where appropriate. A strategy can have a high win rate and lose money because its average losses exceed its average wins and costs. Available historical bars/report features may depend on your TradingView plan. No subscription purchase is required merely to paste the code; feature eligibility must be checked in your account.

## 6. Enable buy/sell/close notifications

1. Ensure BROBS is added to the intended symbol/timeframe chart.
2. Click **Create alert** (or use the strategy report's Add Alert action).
3. Select **BROBS Multi-Market Paper** as the condition.
4. Choose **Order fills only**.
5. In Message, enter exactly:

```text
{{strategy.order.alert_message}}
```

6. Choose a name such as **BROBS BTCUSDT 1H paper** and enable app/email notifications as available in your account.
7. Create the alert. Do this separately for each symbol; an alert on EURUSD does not also monitor AAPL/BTCUSDT.
8. Delete/recreate the alert after modifying script code, inputs, dates, symbol or timeframe. TradingView alerts run a saved snapshot.

Notifications contain app, chart ticker, quote currency, timeframe, signal time, action (buy/sell/close) and `paper_only: true`. The timestamp identifies the signal bar, not necessarily the later fill. Stop/target notifications indicate a closed emulator trade. Alerts are not guaranteed fills and are not broker-account confirmations. Historical trades do not retroactively send live alerts.

## 7. Connection to BROBS or a broker

The Python runners poll their own feeds and maintain their own SQLite accounts. TradingView and Python simulations may differ. This release provides **notifications**, not a publicly deployed forex/stock/crypto webhook-to-runner adapter. The older `brobs.alerts` localhost demo has a different payload and rejects forex; this Pine JSON must not be sent to it as if integration were complete.

TradingView webhook delivery requires an eligible alert configuration, two-factor authentication and a publicly reachable endpoint using supported ports 80/443. No endpoint is deployed by this change. Never paste brokerage keys into Pine code or alert messages. No real-money order connection is supplied.

## 8. Why TradingView and Python results differ

Signals use confirmed bars, with market orders normally filling at the next bar open. No future-looking data requests are used. Brackets are submitted with entries using signal-close tick distances; Python stops use the actual entry price, so gaps differ. Pine uses its own intrabar fill assumptions, while Python assumes stop first if both levels touch. Python research spread is constant within each bar, scaled from that bar's open. Pine uses chart-feed data and fixed tick slippage/percentage commission approximations; historical dividends, swaps, cash settlement and liquidity are not modeled by the Python research. Pine Wilder RSI uses the full chart history; Python uses up to 500 preceding bars, so initialization can differ. Pine's intraday risk rule follows the chart session rather than the Python UTC day, and halt-reset behavior differs. Bar Magnifier, if available, can improve intrabar detail but cannot verify broker execution. Backtests are evidence about their assumptions, not future odds.

Official references:
- https://www.tradingview.com/support/solutions/43000711497-how-to-create-new-script/
- https://www.tradingview.com/pine-script-docs/concepts/strategies/
- https://www.tradingview.com/support/solutions/43000481368-strategy-alerts/
- https://www.tradingview.com/pine-script-docs/concepts/alerts/
- https://www.tradingview.com/support/solutions/43000529348-how-to-configure-webhook-alerts/

## A $10 paper account

In strategy **Settings → Properties**, change Initial capital to 10. This does not deposit money or connect a broker. On BTCUSDT/ETHUSDT the balance is 10 USDT. Keep costs enabled and risk/notional limits unchanged. At the default 20% notional cap, the entry budget starts at about 2 quote-currency units; whole-share stock entries will usually round to zero. The chart status now explains this minimum-quantity block. RSI2 thresholds up to 49 are accepted, including the Python lab's 35 profile. These changes have not been compiled inside TradingView here.

The Python crypto runner now also accepts custom paper capital:

```bash
python -m brobs.market_runner --market crypto --capital 10 --db brobs_crypto_10.db --once
```

This polls public data but simulates fills locally. Repeat the same capital setting when reopening that database; use a new database for a different starting balance. Add `--demo` for synthetic data rather than public quotes. For forex, the existing `brobs.fx_runner --capital 10` requires OANDA practice credentials unless `--demo` is used. Small-unit paper fills do not establish the minimum trade size accepted by a real venue.

BROBS has no verified future win probability or intraday profit forecast. Its real-money execution remains disabled; a $10 simulation cannot earn real cash by tonight. Testing a historical period at $10 is useful for checking sizing, not forecasting today's return.
