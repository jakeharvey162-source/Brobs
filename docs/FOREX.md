# Forex implementation

Use `python -m brobs.fx_runner` and `python -m brobs.app`. See the root README for setup and thresholds.

## Implemented and tested

- OANDA v20 practice-only GET adapter: completed candles, account summary, current bid/ask.
- USD account / EUR_USD, GBP_USD, AUD_USD, NZD_USD restrictions. Other conversions fail closed.
- Local long/short P&L in quote USD, spread/slippage/optional commission, stop/take profit, full notional reserve without leverage.
- Freshness, tradeable-market, valid numeric data and complete marks required before mutations.
- Atomic SQLite state + events + closed trades; concurrent workers serialize and deduplicate.
- Completed-candle signals once per bar; stops still evaluated on subsequent quotes for that bar.
- Persistent pause, daily-loss and peak-drawdown controls; automated polling and recorded health.
- Browser-tested read-only localhost dashboard; no broker token appears in dashboard state.

## Important boundaries

This is **broker-data-connected local simulation**, not broker-hosted paper order execution. No POST/PUT order endpoints are present. Practice credentials have not been available for end-to-end provider validation. Eligibility must be checked with the provider.

No overnight swaps, broker margin calls, leverage, market-depth liquidity, partial fills or execution acknowledgements. Polling cannot enforce guaranteed loss ceilings. The old `forex_runner` intentionally remains research-only for backward compatibility.
