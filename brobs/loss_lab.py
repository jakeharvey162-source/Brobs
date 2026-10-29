"""Loss-aware historical paper-research diagnostics; never submits orders.

The earlier portion generates training loss profiles. The later period
is reported without changing strategy parameters or executing trades.
"""
import argparse
import csv
import hashlib
import json
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from math import isfinite
from pathlib import Path
from statistics import mean, pstdev
from urllib.parse import urlsplit

from .fx_research import load_forex_csv, replay
from .historical_validation import validate_rows

UTC = timezone.utc
MIN_BUCKET_TRADES = 8
FOREX_BAR_DURATION = timedelta(hours=1)


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


def _validated_news(news):
    """Validate direct callers as well as CSV input; metadata is not truth."""
    events = []
    for row in news:
        if not isinstance(row, dict):
            raise ValueError("News event must be a mapping")
        try:
            published = timestamp(row["published_at"])
            available = timestamp(row["available_at"])
            url, label = row["source_url"], row["event_label"]
        except (KeyError, TypeError) as exc:
            raise ValueError("News event missing required fields") from exc
        if not isinstance(url, str) or not isinstance(label, str):
            raise ValueError("Invalid news provenance or event label")
        url, label = url.strip(), label.strip()
        parsed = urlsplit(url)
        if (available < published or parsed.scheme != "https" or not parsed.hostname
                or parsed.username is not None or parsed.password is not None):
            raise ValueError("Invalid news provenance or timing")
        if not label or len(label) > 160:
            raise ValueError("Invalid event label")
        events.append(dict(published_at=published, available_at=available,
                           source_url=url, event_label=label))
    return sorted(events, key=lambda item: (item["available_at"], item["published_at"],
                                           item["source_url"], item["event_label"]))


def load_news_metadata(path):
    """Load optional user-supplied historical metadata; no news is verified."""
    if path is None:
        return []
    with open(path, newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        required = {"published_at", "available_at", "source_url", "event_label"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("News CSV missing required columns")
        return _validated_news(reader)


class _NewsIndex:
    """Index availability once; existence queries cost O(log news rows)."""
    def __init__(self, news, max_age_hours=24):
        if (isinstance(max_age_hours, bool)
                or not isinstance(max_age_hours, (int, float))
                or not isfinite(max_age_hours) or max_age_hours <= 0):
            raise ValueError("News age window must be positive and finite")
        try:
            self.window = timedelta(hours=max_age_hours)
        except OverflowError as exc:
            raise ValueError("News age window is too large") from exc
        self.events = _validated_news(news)
        self.available_at = [item["available_at"] for item in self.events]
        self.latest_expiry = []
        latest = None
        for item in self.events:
            try:
                expiry = item["published_at"] + self.window
            except OverflowError as exc:
                raise ValueError("News timestamp exceeds supported date range") from exc
            latest = expiry if latest is None else max(latest, expiry)
            self.latest_expiry.append(latest)

    def has_available(self, when):
        last = bisect_right(self.available_at, when) - 1
        return last >= 0 and self.latest_expiry[last] >= when

    def available(self, when):
        first = bisect_left(self.available_at, when - self.window)
        last = bisect_right(self.available_at, when)
        # Late ingestion cannot make an old publication fresh again.
        return [item for item in self.events[first:last]
                if when - item["published_at"] <= self.window]


def available_news(news, at, max_age_hours=24):
    """Exclude future and stale publication AND availability timestamps."""
    return _NewsIndex(news, max_age_hours).available(timestamp(at))


class _HistoryIndex:
    """Precompute bar completion times once, not once per closed trade."""
    def __init__(self, rows, bar_duration=FOREX_BAR_DURATION):
        if not isinstance(bar_duration, timedelta) or bar_duration <= timedelta(0):
            raise ValueError("A positive bar duration is required")
        self.rows = validate_rows(rows, min_rows=1)
        self.completed_at = [row["timestamp"] + bar_duration for row in self.rows]
        self.closes = [row["close"] for row in self.rows]

    def regime(self, when):
        prior_count = bisect_right(self.completed_at, when)
        if prior_count < 101:
            return "insufficient_prior_bars"
        closes = self.closes[prior_count - 101:prior_count]
        gap = mean(closes[-8:]) / mean(closes[-21:]) - 1
        trend = "up" if gap > .0001 else "down" if gap < -.0001 else "mixed"
        returns = [b / a - 1 for a, b in zip(closes, closes[1:])]
        near, prior = pstdev(returns[-20:]), pstdev(returns)
        volatility = "elevated" if prior > 0 and near > prior * 1.5 else "ordinary"
        return trend + "/" + volatility


def entry_regime(rows, at, *, bar_duration=FOREX_BAR_DURATION):
    """Categorize completed candles only; a current candle's close is unknown."""
    return _HistoryIndex(rows, bar_duration).regime(timestamp(at))


def _profile(trades, history, news_index):
    buckets = defaultdict(list)
    reasons, loss_reasons = Counter(), Counter()
    news_seen = 0
    closed_trades = 0
    for trade in trades:
        if not isinstance(trade, dict):
            raise ValueError("Trade result must be a mapping")
        try:
            opened, closed = timestamp(trade["opened_at"]), timestamp(trade["closed_at"])
            pnl = trade["pnl"]
        except KeyError as exc:
            raise ValueError("Trade result missing required fields") from exc
        if (closed < opened or isinstance(pnl, bool)
                or not isinstance(pnl, (int, float)) or not isfinite(pnl)):
            raise ValueError("Invalid trade result")
        buckets[history.regime(opened)].append(pnl)
        reason = trade.get("reason", "unknown")
        if not isinstance(reason, str):
            raise ValueError("Invalid trade exit reason")
        reasons[reason] += 1
        if pnl < -1e-9:
            loss_reasons[reason] += 1
        closed_trades += 1
        if news_index.has_available(opened):
            news_seen += 1
    result = []
    for regime, pnls in sorted(buckets.items()):
        wins = sum(p > 1e-9 for p in pnls)
        losses = sum(p < -1e-9 for p in pnls)
        net = sum(pnls)
        result.append(dict(regime=regime, trades=len(pnls), wins=wins, losses=losses,
                           breakeven=len(pnls) - wins - losses,
                           net_pnl=round(net, 4),
                           observed_win_pct=round(100 * wins / len(pnls), 2),
                           review_flag=(len(pnls) >= MIN_BUCKET_TRADES
                                        and losses > wins and net < 0)))
    return dict(buckets=result, closed_trades=closed_trades,
                loss_reasons=dict(sorted(loss_reasons.items())),
                exit_reasons=dict(sorted(reasons.items())),
                entries_with_prior_news_metadata=news_seen,
                caveat="Historical research only; news metadata not independently verified")


def profile(trades, rows, news=(), *, bar_duration=FOREX_BAR_DURATION):
    """Diagnostic loss groups, never future probabilities.

    Validate/index bars once and sort/index news once. Per-trade lookup is
    O(log bars + log news) plus a fixed 101-candle regime window, rather
    than rescanning every candle and news event for each trade.
    """
    return _profile(trades, _HistoryIndex(rows, bar_duration), _NewsIndex(news))


def evaluate(rows, news=()):
    """Compare fixed strategy training and reused later period; no promotion."""
    rows = validate_rows(rows, min_rows=600)
    history, news_index = _HistoryIndex(rows), _NewsIndex(news)
    count = len(rows)
    start, cutoff = int(count * .3), int(count * .7)
    earlier = replay(rows[:cutoff], start, include_trades=True)
    later = replay(rows, cutoff, include_trades=True)
    earlier_trades = earlier.pop("trades")
    later_trades = later.pop("trades")
    earlier_profile = _profile(earlier_trades, history, news_index)
    later_profile = _profile(later_trades, history, news_index)
    flags = [b["regime"] for b in earlier_profile["buckets"] if b["review_flag"]]
    followup = [b for b in later_profile["buckets"] if b["regime"] in flags]
    return dict(
        version=1, mode="READ_ONLY_HISTORICAL_PAPER_RESEARCH",
        execution_enabled=False,
        validation_status="not_validated",
        holdout_status="previously_inspected_contaminated",
        selected_parameters=None, cash_fallback=True,
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
        news=dict(metadata_rows=len(news_index.events),
                  entries_with_pre_entry_metadata=later_profile["entries_with_prior_news_metadata"],
                  metadata_provenance="user_supplied_not_independently_verified",
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
    if args.news_csv:
        result["news_input_sha256"] = hashlib.sha256(Path(args.news_csv).read_bytes()).hexdigest()
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
