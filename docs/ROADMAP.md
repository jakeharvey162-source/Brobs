# BROBS implementation status

## Implemented
- OHLCV historical CSV ingestion with ordering and validity checks
- Simple chronological SMA backtest with next-bar-open execution, estimated fees and slippage
- Baseline optional scikit-learn direction classifier with chronological holdout and baseline accuracy comparison
- Read-only localhost HTML dashboard for JSON reports
- Paper-only simulator and unit tests

## Not implemented / not validated
- No broker/exchange connectors, no credential storage, no live trading or unattended daemon
- No live streaming data; user must supply licensed real OHLCV CSV data
- No validated profitable strategy; ML accuracy is not a trading return metric
- No walk-forward optimizer, corporate actions, dividends, shorting, leverage, FX lot/pip handling, overnight swaps, market calendars, or reliable intrabar stop fills
- No durable position persistence or trade reconciliation; no security review or production monitoring

## Historical research usage
```bash
python -m brobs.cli --csv YOUR_REAL_CANDLES.csv --market stock --symbol AAPL > report.json
python -m brobs.dashboard --report report.json
# open http://127.0.0.1:8765
```
CSV must have timestamp,open,high,low,close,volume headers; UTC or offset timestamps recommended. Import genuine licensed data yourself; synthetic demo data must not be treated as historical evidence.

Optional model: `pip install scikit-learn`, then call `evaluate_direction_model(closes)` on >=100 historical closes.

## Broker connection plan
Use official broker APIs with read-only connectivity first. Candidate integrations require user-chosen regulated broker/exchange, account eligibility, instrument specs, explicit risk approval, sandbox testing, secret management and kill switches. Never store credentials in GitHub. TradingView is not required.
