# Reproducible comparisons

Run `python -m brobs.fx_research --csv research/data/EURUSD_1h.csv`. Default parameters are fixed before chronological holdout evaluation. Signals use only bars preceding the fill bar; entries use next-bar open. Intrabar ambiguity takes the stop first. Final positions are liquidated. Reported cost assumptions are included in JSON.

Read `research/eurusd-holdout.json` for the 949-bar holdout, higher-cost stress and three independent holdout subperiods. There is no parameter optimizer or selection on this holdout. Do not keep tuning to this sample and treat it as unseen data.

`python -m brobs.reference --csv ...` invokes the actual public Backtrader engine with a simple SMA reference. Differences in bracket handling and costs are disclosed; it is an implementation reference, not proof BROBS beats Backtrader strategies, Freqtrade or experienced traders.

Win/loss counts refer only to closed simulated trades. Wilson intervals describe the sample proportion under simplifying independence assumptions; trades are not necessarily independent. Fewer than 100 trades is labeled insufficient evidence, and 100 trades alone would still not prove a robust edge. Profit factor = positive closed-trade P&L / absolute negative P&L. Undefined ratios are null, not fabricated infinity.

Optional sklearn evaluation is in `research/ml-evaluation.json`. Accuracy below the majority baseline is not predictive advantage. No real brokerage funds were used.
