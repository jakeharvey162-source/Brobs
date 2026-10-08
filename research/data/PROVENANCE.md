# EURUSD sample provenance

Source: https://github.com/getdata-finance/eurusd-1h-ohlcv-forex-historical-data/blob/main/EURUSD_1h.csv

Retrieved 2026-10-08. Git blob SHA: `25c7ac652f23d23a83eeea4a8f5c237179aed15c`. 3,162 hourly rows, 2026-03-26 through 2026-09-25. `datetime` is the vendor's bar-open UTC timestamp; volume is tick volume.

License: MIT; the complete copyright and permission notice is preserved in `GETDATA-LICENSE.txt`. This is a public vendor evaluation sample, not independently certified data. No vendor quality or completeness claims are adopted by BROBS.

Only this sample is included, not any paid archive. CSV timestamps, finite positive OHLC, valid ranges, nonnegative volume and ordering were validated. Historical simulations assume a fixed spread because this CSV does not contain historical executable bid/ask quotes.

## Stock sample

`AAPL_1d.csv` normalizes the Date and raw AAPL OHLCV columns from Plotly `finance-charts-apple.csv`, blob `7b1bab3953bb5cdf47e84de1048ca04b0c991987`, https://github.com/plotly/datasets/blob/master/finance-charts-apple.csv. 506 daily bars, 2015-02-17 through 2017-02-16. Repository MIT notice retained in `PLOTLY-LICENSE.txt`. Precomputed technical columns and adjusted close are not used. Old raw-price data; dividends/corporate actions are not modeled and sample results are not current stock performance.

## Crypto archive evaluation

The BTCUSDT sample is downloaded directly from Binance public spot archives for 2026-01 through 2026-09, hourly, 6,552 contiguous bars. The downloader validates each archive SHA-256 against its `.CHECKSUM` before normalizing milliseconds/microseconds and OHLCV. Source URLs/checksums and normalized-file digest are in `BTCUSDT_1h.provenance.json`. The full archive data is not redistributed in this repo; reproduce it using `brobs.public_data`. USDT is not USD. Sources: https://data.binance.vision/ and https://github.com/binance/binance-public-data. Archive integrity does not imply profitable signals.
