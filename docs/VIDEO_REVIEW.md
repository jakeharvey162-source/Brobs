# Video review and 70% experiment

Reviewed the supplied 40-second video on 2026-10-09. It shows @ZACK.S.T.A, a post attributed to @0xboan about $87 becoming $8,391, and Chief/Scout/News/Sentiment/Charts/Skeptic roles. It does not supply the complete closed-trade ledger, deposits/withdrawals, losing runs, fees, executable strategy or an independently reproducible evaluation. The displayed profit claim is not a measured probability of winning the next trade. I could not establish an exact public repository for that video.

## Public source examined

[zostaff/grok-trading-desk](https://github.com/zostaff/grok-trading-desk/tree/ec900a85a8a0fbb6123ee100b5c10d48e25fdcdb), pinned to `ec900a85a8a0fbb6123ee100b5c10d48e25fdcdb`, contains twelve desk roles plus a shared exit manager. Reviewed `src/stocks/stock_checker.py`, `scripts/replay.py` and the README. The checker argues against an entry and defaults to rejection on failure. Its replay script summarizes a supplied event log; it is not a historical strategy backtester and no verified 70% ledger was found in this review. The repository tree had no license file, so no source was imported. The README describes experimental paper-first software; some execution components require users to wire their own implementation.

BROBS now independently strengthens its existing optional Grok review prompt: challenge trend disagreement, volatility relative to the fixed stop, extension, costs and missing evidence. Agreement between several agents is not treated as statistical proof. The model still cannot change risk settings or send orders. This is a review change, not a demonstrated improvement in win rate. No paid API request was made, and BROBS does not run the upstream desk or the video's bots.

## Declared experiment

`brobs.winrate_lab` evaluates exactly 16 existing RSI2 profiles: thresholds 5/10/20/35, half/default stop distance, and reward/risk 1/2. Risk sizing, notional limits, fees and stops remain active. It does not shrink reward/risk below 1 merely to manufacture a high hit rate.

Selection uses only two earlier chronological validation segments: each needs at least 15 closed trades, positive net P/L and profit factor >=1.1; the combined training segment must also profit under stressed costs. Rank by the weaker segment's net return, then combined P/L. When none qualifies, selection is cash. Later-period results for every fixed candidate are reported, never used to choose the candidate.

The count diagnostic recomputes observed wins and the Wilson 95% interval from integer trade counts. Its historical count gate requires at least 100 trades and a lower interval bound strictly above 70%. Even a passed count gate would not establish future win probability: trade dependence, changing regimes and repeated searches invalidate that shortcut. Profitable stressed results and separate chronological stability are also needed. All data periods in this experiment have already been inspected, so reports explicitly remain exploratory and cannot authorize entries through the research evidence gate.

Committed reports: `research/winrate-btc-evaluation.json`, `research/winrate-eth-evaluation.json`, `research/winrate-forex-evaluation.json`. Input SHA256 values bind them to exact CSVs. BTC uses 21 months of hourly bars; ETH nine months; EURUSD the existing 3,162-hour sample. Historical Grok/news/sentiment decisions were not reconstructed. Stock support remains available in the paper runner, but its old daily example is not adequate for a current stock-performance claim.

All three training selections returned cash; none of the 48 later-period comparisons passed the historical count gate. Highest observed later-period hit rates below are descriptive comparisons, not selected or approved profiles:

| Market | Wins / closed trades | Observed win rate | Net return after costs | Wilson 95% interval |
| --- | --- | --- | --- | --- |
| BTC/USDT | 32 / 102 | 31.37% | -4.8868% | 23.18–40.91% |
| ETH/USDT | 9 / 19 | 47.37% | -0.4670% | 27.33–68.29% |
| EUR/USD | 10 / 19 | 52.63% | -0.0119% | 31.71–72.67% |

132 local unit/integration tests passed. The EURUSD experiment was rerun independently and its report matched byte for byte; CI also checks reproduction. No 70% future probability is verified and no new profile was promoted.

Reproduce with no API key:

```bash
python -m unittest discover -s tests -v
python -m brobs.winrate_lab --csv research/data/EURUSD_1h.csv --market forex --symbol EUR_USD --output /tmp/winrate-forex-evaluation.json
diff research/winrate-forex-evaluation.json /tmp/winrate-forex-evaluation.json
```

For locally downloaded crypto CSVs, substitute the CSV path, `--market crypto` and `--symbol BTC_USDT` or `ETH_USDT`. Existing `brobs.public_data` and `brobs.history_merge` reproduce the archived inputs described in `docs/PRO_COMPARISON.md`.

An improvement developed after examining these results needs a newly frozen specification and fresh evaluation data. Repeatedly altering it against the same later period until the displayed percentage reaches 70 would measure fitting to that sample, not a solid chance of winning. Real-money orders remain disabled.
