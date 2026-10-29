"""Loss-aware historical paper-research diagnostics; never submits orders.

The earlier portion generates training loss profiles. The later period
is reported without changing strategy parameters or executing trades.
"""
import argparse
import csv
import hashlib
import json
from bisect import bisect_left
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from math import isfinite
from pathlib import Path
from statistics import mean, pstdev
from urllib.parse import urlsplit

from .fx_research import load_forex_csv, replay

UTC = timezone.utc
MIN_BUCKET_TRADES = 8


def timestamp(value):
    """Require an explicit UTC offset, especially for archived news."""
    if isinstance(value, datetime):
        stamp = value
    elif isinstance(value, str):
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ValueError("Timestamp must be a datetime or ISO string")
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise ValueError("Timestamp requires an explicit timezone")
    return stamp.astimezone(UTC)


def load_news_metadata(path):
    """Load optional user-supplied historical metadata; no news is verified."""
    if path is None:
        return []
    events = []
    with open(path, newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        required = {"published_at", "available_at", "source_url", "event_label"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("News CSV missing required columns")
        for row in reader:
            published = timestamp(row["published_at"])
            available = timestamp(row["available_at"])
            url = (row["source_url"] or "").strip()
            label = (row["event_label"] or "").strip()
            parsed = urlsplit(url)
            if available < published or parsed.scheme != "https" or not parsed.hostname:
                raise ValueError("Invalid news provenance or timing")
            if not label or len(label) > 160:
                raise ValueError("Invalid event label")
            events.append(dict(published_at=published, available_at=available,
                               source_url=url, event_label=label))
    return sorted(events, key=lambda item: item["available_at"])


def available_news(news, at, max_age_hours=24):
    """Exclude both future publication and delayed ingestion."""
    when = timestamp(at)
    window = timedelta(hours=max_age_hours)
    return [item for item in news
            if item["published_at"] <= item["available_at"] <= when
            and when - item["available_at"] <= window]


def entry_regime(rows, at):
    """Categorize only closed bars STRICTLY preceding entry."""
    when = timestamp(at)
    prior_count = bisect_left([timestamp(row["timestamp"]) for row in rows], when)
    if prior_count < 101:
        return "insufficient_prior_bars"
    closes = [r["close"] for r in rows[prior_count - 101:prior_count]]
    if any(not isfinite(x) or x <= 0 for x in closes):
        raise ValueError("Invalid historical prices")
    gap = mean(closes[-8:]) / mean(closes[-21:]) - 1
    trend = "up" if gap > .0001 else "down" if gap < -.0001 else "mixed"
    returns = [b / a - 1 for a, b in zip(closes, closes[1:])]
    near, prior = pstdev(returns[-20:]), pstdev(returns)
    volatility = "elevated" if prior > 0 and near > prior * 1.5 else "ordinary"
    return trend + "/" + volatility


def profile(trades, rows, news=()):
    """Diagnostic loss groups, never future probabilities."""
    buckets = defaultdict(list)
    reasons = Counter()
    news_seen = 0
    for trade in trades:
        opened, closed = timestamp(trade["opened_at"]), timestamp(trade["closed_at"])
        pnl = trade["pnl"]
        if (closed < opened or isinstance(pnl, bool)
                or not isinstance(pnl, (int, float)) or not isfinite(pnl)):
            raise ValueError("Invalid trade result")
        buckets[entry_regime(rows, opened)].append(pnl)
        reasons[trade.get("reason", "unknown")] += 1
        if available_news(news, opened):
            news_seen += 1
    result = []
    for regime, pnls in sorted(buckets.items()):
        wins = sum(p > 1e-9 for p in pnls)
        losses = sum(p < -1e-9 for p in pnls)
        net = sum(pnls)
        result.append(dict(regime=regime, trades=len(pnls), wins=wins, losses=losses,
                           net_pnl=round(net, 4),
                           observed_win_pct=round(100 * wins / len(pnls), 2),
                           review_flag=(len(pnls) >= MIN_BUCKET_TRADES
                                        and losses > wins and net < 0)))
    return dict(buckets=result, closed_trades=len(trades),
                loss_reasons=dict(sorted(reasons.items())),
                entries_with_prior_news_metadata=news_seen,
                caveat="Historical research only; news metadata not independently verified")


def evaluate(rows, news=()):
    """Compare fixed strategy training and reused later period; no promotion."""
    if len(rows) < 600:
        raise ValueError("At least 600 historical bars are required")
    for earlier, later in zip(rows, rows[1:]):
        if timestamp(earlier["timestamp"]) >= timestamp(later["timestamp"]):
            raise ValueError("Chronological data required")
    count = len(rows)
    start, cutoff = int(count * .3), int(count * .7)
    earlier = replay(rows[:cutoff], start, include_trades=True)
    later = replay(rows, cutoff, include_trades=True)
    earlier_trades = earlier.pop("trades")
    later_trades = later.pop("trades")
    earlier_profile = profile(earlier_trades, rows[:cutoff], news)
    later_profile = profile(later_trades, rows, news)
    flags = [b["regime"] for b in earlier_profile["buckets"] if b["review_flag"]]
    followup = [b for b in later_profile["buckets"] if b["regime"] in flags]
    return dict(
        version=1, mode="READ_ONLY_HISTORICAL_PAPER_RESEARCH",
        execution_enabled=False,
        source="BROBS existing fixed-parameter forex research strategy",
        train=dict(start=timestamp(rows[start]["timestamp"]).isoformat(),
                   last_bar=timestamp(rows[cutoff - 1]["timestamp"]).isoformat(),
                   baseline=earlier, loss_profile=earlier_profile),
        later=dict(first_bar=timestamp(rows[cutoff]["timestamp"]).isoformat(),
                   last_bar=timestamp(rows[-1]["timestamp"]).isoformat(),
                   baseline=later, loss_profile=later_profile),
        loss_learning=dict(
            training_only_review_flags=flags,
            later_outcomes_in_flagged_regimes=followup,
            outcome="Diagnostic watchlist only; strategy and risk parameters unchanged",
            minimum_bucket_trades=MIN_BUCKET_TRADES),
        news=dict(metadata_rows=len(news),
                  entries_with_pre_entry_metadata=later_profile["entries_with_prior_news_metadata"],
                  limitation="No news fetched; future publication/availability never included. Unexpected public statements cannot be forecast."),
        limitations=[
            "Later EURUSD period has already been inspected in past BROBS research; not an unseen test",
            "Loss patterns are descriptive and do not establish a learning advantage",
            "No broker orders, live adaptation or real-money execution",
            "OHLC stop-first assumptions, swaps, liquidity and partial fills remain limitations",
        ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--news-csv", help="Optional archived news-event metadata CSV")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = load_forex_csv(args.csv)
    result = evaluate(rows, load_news_metadata(args.news_csv))
    result["input_sha256"] = hashlib.sha256(Path(args.csv).read_bytes()).hexdigest()
    Path(args.output).write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "mode": result["mode"],
        "training_closed": result["train"]["baseline"]["closed_trades"],
        "training_wins": result["train"]["baseline"]["wins"],
        "later_closed": result["later"]["baseline"]["closed_trades"],
        "later_wins": result["later"]["baseline"]["wins"],
        "later_net_pnl": result["later"]["baseline"]["net_pnl"],
        "training_watchlist": result["loss_learning"]["training_only_review_flags"],
        "report": args.output,
        "not_future_win_probability": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
