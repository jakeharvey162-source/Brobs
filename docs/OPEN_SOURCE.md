# Public foundations actually used

- **Backtrader 1.9.78.123** — https://github.com/mementum/backtrader. Optional imported research engine in `brobs/reference.py`; its actual engine was run on the included sample. GPL-3.0, installed separately; no Backtrader source is vendored.
- **scikit-learn** — https://github.com/scikit-learn/scikit-learn. Optional imported local logistic classifier and scaler in `ml.py` / `ml_agent.py`. BSD-3-Clause, installed separately. No claimed predictive edge.
- **GetData EURUSD hourly sample** — MIT-licensed data; source/blob identity and complete notice in `research/data/`.
- **Freqtrade documentation** — https://www.freqtrade.io/en/stable/lookahead-analysis/ informed the emphasis on leakage checks. No Freqtrade code or trained model is integrated.
- **OANDA v20 documentation** — https://developer.oanda.com/rest-live-v20/pricing-ep/ and practice REST API schemas guided the read-only adapter. Broker service eligibility and availability are separate from this source code.

QuantConnect LEAN, FreqAI and Qlib remain potential future evaluations; they are not falsely described as installed engines. Installing a public repo does not import a profitable strategy.
