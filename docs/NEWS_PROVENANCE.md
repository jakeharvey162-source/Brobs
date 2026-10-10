# BROBS: no-cost news provenance and conservative sentiment gate

**Status:** Implemented as an **opt-in, paper-only** gate for BTC_USDT, ETH_USDT, AAPL and MSFT in `market_runner`. It does not place real orders, infer a reliable probability of profit, verify the truth of a news report, or promise a positive return. There is no verified forward performance attributable to this module.

## How it works

The new `brobs/news_sentiment.py` uses the free GDELT DOC 2.0 article-list metadata endpoint, through the Python standard library. No paid API key or LLM is needed. It queries a fixed whitelisted asset name, not an arbitrary user-supplied URL. Requests use HTTPS, an eight-second timeout, a 400 KB response cap, and refuse redirects. It fetches metadata only, **not article bodies**.

For each candidate article, BROBS checks:
1. HTTPS publisher URL and a matching GDELT-reported domain, on the explicit publisher allowlist. `www.` subdomains are allowed; misleading domains such as `reuters.com.attacker.invalid` are not.
2. GDELT article **seen** time (not necessarily the original publication time) no more than 24 hours old and not future-dated.
3. English-language metadata and a headline explicitly mentioning the supported asset.
4. Unique article URLs and coverage by at least **two different allowed publisher domains** (two headlines from the same outlet count only once).
5. Simple disclosed title-keyword sentiment. This deliberately limited lexicon is **not an audited financial sentiment model** or predictor.

The result includes publisher names, original links, dates, and a label: `positive`, `negative`, `mixed`, `neutral`, or `unknown`. Even `verified_metadata` means **source metadata meets the configured rules**, not that the articles or sentiment are correct. GDELT can miss articles or report inaccurate metadata. Two outlets may also repeat one original story. Neutral or positive headlines are **not buy signals**.

When `--news-guard` is activated and technical indicators propose a **new** paper entry:
- Negative corroboration or conflicting evidence: **HOLD / veto**.
- Provider error, unsupported symbol, stale/missing items, insufficient publisher diversity: **HOLD / veto**.
- Two or more sufficiently fresh reputable sources without an adverse/mixed classification: allows the independent *technical* signal to proceed through BROBS's existing sizing, risk, and evidence checks; it does **not** initiate a trade by itself.
- Existing positions and protective exits are processed by the normal price/stop logic without consulting GDELT. An internet outage in news retrieval must never suppress an exit.

The gate defaults to **OFF**. It is experimental. Very limited coverage may prevent most trades. No out-of-sample improvement has been demonstrated. The forex runner does not use this feed because a pair-specific directional interpretation of macro news has not been validated.

## Inspect the feed yourself

```bash
python -m brobs.news_sentiment --symbol BTC_USDT
python -m brobs.news_sentiment --symbol ETH_USDT
python -m brobs.news_sentiment --symbol AAPL
```

This prints a JSON provenance report and exits nonzero if coverage is insufficient or the upstream service is unavailable. No simulated or live broker order is placed by the inspection command.

## Turn on the gate in local *paper* trading

Requires existing verified market-data configuration when `--demo` is absent. Follow the root README for the runner's other prerequisites.

```bash
python -m brobs.market_runner --market crypto --symbols BTC_USDT --db guarded_news_crypto.db --strategy trend --news-guard
python -m brobs.app --market crypto --db guarded_news_crypto.db
```

Stop with Ctrl+C. To test the interface without market provider credentials, use `--demo --once`. That demo's market prices remain synthetic, and external GDELT coverage is not proof of anything in those prices.

**No free live-trading API, no autonomous real-money orders, and no backtested profitability have been established by adding a news feed.** Combining disparate headline and technical signals may *reduce* performance. Controlled evaluation against the original strategy and newer unseen market history is still required.

## Verification tests

Run `python -m unittest discover -s tests -v`. The fixture tests reject stale, future, unrelated, duplicated and spoofed publisher records; reject unavailable GDELT responses; exercise mixed/negative headlines and entry vetoes; confirm positive coverage never bypasses the underlying signal; and exercise protective paper stops independently of news retrieval.

## Sources

- Official GDELT DOC 2.0: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
- GDELT JSONFeed feature: https://blog.gdeltproject.org/gdelt-doc-2-0-api-supports-jsonfeed/
- Documented DOC article-list data fields: https://github.com/alex9smith/gdelt-doc-api
