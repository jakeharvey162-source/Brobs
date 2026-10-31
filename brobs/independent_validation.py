"""Offline, falsifiable loss-screen shadow experiment; never places broker orders.

The screen is selected exclusively from earlier trades. Its evaluation replays
both strategies on identical later bars using the unchanged FXBook risk engine.
Previously inspected EURUSD history is *not* independent out-of-sample proof.
"""
import argparse
import hashlib
import json
import math
from datetime import timedelta
from pathlib import Path

from .fx import FXConfig
from .fx_research import load_forex_csv, replay
from .fx_signals import decide
from .loss_lab import entry_regime, evaluate as loss_evaluate, load_news_metadata, timestamp


def audit_bars(rows, expected_interval_hours=1):
    """Check in-memory OHLCV integrity and describe gaps without filling them."""
    if not rows or not math.isfinite(expected_interval_hours) or expected_interval_hours <= 0:
        raise ValueError("Bars and a positive interval are required")
    previous = None
    gaps = []
    for row in rows:
        at = timestamp(row["timestamp"])
        values = [row[key] for key in ("open", "high", "low", "close", "volume")]
        if any(isinstance(v, bool) or not isinstance(v, (int, float))
               or not math.isfinite(v) or v < 0 for v in values):
            raise ValueError("Non-finite or negative OHLCV")
        op, high, low, close, _ = values
        if min(op, high, low, close) <= 0 or low > min(op, close) or high < max(op, close):
            raise ValueError("Inconsistent historical OHLC range")
        if previous is not None:
            elapsed = (at - previous).total_seconds() / 3600
            if elapsed <= 0:
                raise ValueError("Duplicate or out-of-order historical timestamp")
            if elapsed > expected_interval_hours * 1.5:
                gaps.append(round(elapsed, 6))
        previous = at
    return dict(rows=len(rows), first_bar=timestamp(rows[0]["timestamp"]).isoformat(),
                last_bar=previous.isoformat(), expected_interval_hours=expected_interval_hours,
                gap_count=len(gaps), largest_gap_hours=max(gaps, default=0),
                gaps_not_filled=True,
                warning="Gaps may be market closures or missing data; require vendor verification")


def screening_signal(history, side, forbidden_regimes, counters=None):
    """Use preceding bars ONLY. Never veto management or exits of open positions."""
    action, votes = decide([bar["close"] for bar in history[-200:]])
    if side == 0 and action in ("buy", "sell") and forbidden_regimes:
        if not history:
            return action, votes
        # Entry is at the NEXT bar's open; this instant is strictly after the
        # most recent completed input bar, never after any target entry bar.
        prior_regime = entry_regime(
            history, timestamp(history[-1]["timestamp"]) + timedelta(microseconds=1))
        if prior_regime in forbidden_regimes:
            if counters is not None:
                counters["vetoed_entry_signals"] += 1
            return "hold", votes
    return action, votes


def screened_replay(rows, cutoff, regimes, *, stress=False):
    """Paper-only replay with the identical fills/risk logic and optional cost stress."""
    count = {"vetoed_entry_signals": 0}
    def past_only_signal(history, side):
        return screening_signal(history, side, regimes, count)

    config = FXConfig(commission_fraction=.00005) if stress else None
    result = replay(rows, cutoff, row_signal_fn=past_only_signal,
                    spread=.0003 if stress else .00015, config=config)
    return result, count["vetoed_entry_signals"]


def compare_shadow(rows, news=()):
    """Compare an unmodified baseline with a training-only diagnostic veto.

    No automatic strategy promotion: the later reference was previously examined.
    """
    quality = audit_bars(rows)
    report = loss_evaluate(rows, news)
    cutoff = int(len(rows) * .7)
    regimes = frozenset(report["loss_learning"]["training_only_review_flags"])
    base = report["later"]["baseline"]
    if not regimes:
        candidate, vetoes = dict(base), 0
    else:
        candidate, vetoes = screened_replay(rows, cutoff, regimes)
    stressed_base = replay(rows, cutoff, config=FXConfig(commission_fraction=.00005),
                           spread=.0003)
    if not regimes:
        stressed_candidate, stressed_vetoes = dict(stressed_base), 0
    else:
        stressed_candidate, stressed_vetoes = screened_replay(rows, cutoff, regimes, stress=True)

    difference = round(candidate["return_pct"] - base["return_pct"], 4)
    if not regimes:
        conclusion = "NO_TESTABLE_FILTER: no training regime met the loss flag rule"
    elif vetoes == 0:
        conclusion = "NO_INTERVENTION: trained flags vetoed zero later entry signals"
    elif (candidate["return_pct"] <= base["return_pct"]
          or stressed_candidate["return_pct"] <= stressed_base["return_pct"]):
        conclusion = "FAILED_OR_INCONCLUSIVE: screen did not beat baseline under both cost assumptions"
    else:
        conclusion = "EXPLORATORY_ONLY: numerical advantage on an already-inspected period"
    return dict(version=1, mode="OFFLINE_PAPER_SHADOW_EXPERIMENT",
                execution_enabled=False, auto_promotion=False,
                improved_win_rate_verified=False,
                dataset_audit=quality,
                training=dict(first_bar=report["train"]["start"],
                              last_bar=report["train"]["last_bar"],
                              baseline=report["train"]["baseline"],
                              closed_trades=report["train"]["loss_profile"]["closed_trades"],
                              flagged_regimes=sorted(regimes)),
                evaluation=dict(first_bar=report["later"]["first_bar"],
                                last_bar=report["later"]["last_bar"],
                                inspected_before=True,
                                baseline=base, screened=candidate,
                                baseline_higher_cost=stressed_base,
                                screened_higher_cost=stressed_candidate,
                                vetoed_entry_signals=vetoes,
                                higher_cost_vetoed_entry_signals=stressed_vetoes,
                                return_difference_percentage_points=difference,
                                conclusion=conclusion),
                archived_news_metadata_rows=len(news),
                limitations=[
                    "Training flags selected from training trades only; no later-period optimization",
                    "Previously examined EURUSD holdout, not a fresh independent sample",
                    "Only available-at-before-entry news metadata; no verified archived news supplied",
                    "One EURUSD vendor; missing swaps, venue liquidity and partial fills",
                    "Costs include spread/slippage in fills; separate realized fee amounts unavailable",
                    "Does not combine USD stock and USDT crypto account balances",
                    "No real-money broker integration or policy changes"
                ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--news-csv", help="Optional independently sourced archived-news CSV")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = compare_shadow(load_forex_csv(args.csv), load_news_metadata(args.news_csv))
    result["input_sha256"] = hashlib.sha256(Path(args.csv).read_bytes()).hexdigest()
    Path(args.output).write_text(json.dumps(result, indent=2, allow_nan=False) + "\n",
                                 encoding="utf-8")
    metrics = result["evaluation"]
    print(json.dumps(dict(mode=result["mode"], execution_enabled=False,
                          training_flags=result["training"]["flagged_regimes"],
                          vetoed_entry_signals=metrics["vetoed_entry_signals"],
                          baseline=metrics["baseline"], screened=metrics["screened"],
                          baseline_higher_cost=metrics["baseline_higher_cost"],
                          screened_higher_cost=metrics["screened_higher_cost"],
                          conclusion=metrics["conclusion"], report=args.output),
                     sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
