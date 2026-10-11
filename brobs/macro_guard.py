"""Operator-reviewed macro-event pause for NEW PAPER FX entries only.

An explicit local report can pause a new entry during a high-impact event.
It never generates signals or sends orders, and does not stop protective exits.
Reports are not automatically trusted because an AI or social feed said so.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.parse import urlsplit

MAX_BYTES = 128_000
MAX_REPORT_AGE_SECONDS = 60 * 60

def _utc(value):
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise ValueError("Invalid event time")
    if parsed.tzinfo is None:
        raise ValueError("Timestamps must include UTC or timezone")
    return parsed.astimezone(timezone.utc)

def _hold(signal, reason):
    return {**signal, "action": "hold", "macro_guard": {"decision": "blocked", "reason": reason}}

def gate(signal, report_path, pair, now):
    """Fail closed only when opted in. Closing existing positions is handled upstream."""
    if signal.get("action") not in ("buy", "sell"):
        return signal
    try:
        path = Path(report_path).expanduser().resolve(strict=True)
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            return _hold(signal, "invalid_or_oversized_macro_report")
        report = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(report, dict) or report.get("schema") != "brobs-macro-v1":
            return _hold(signal, "unrecognized_macro_report")
        now = _utc(now)
        as_of = _utc(report["as_of"])
        age = (now - as_of).total_seconds()
        if age < 0 or age > MAX_REPORT_AGE_SECONDS:
            return _hold(signal, "stale_or_future_macro_report")
        if report.get("reviewed") is not True:
            return _hold(signal, "operator_review_required")
        holds = report.get("holds")
        if not isinstance(holds, list) or len(holds) > 100:
            return _hold(signal, "invalid_macro_event_list")
        for event in holds:
            if not isinstance(event, dict):
                return _hold(signal, "malformed_macro_event")
            symbols = event.get("symbols", [])
            if not isinstance(symbols, list) or not all(isinstance(s, str) for s in symbols):
                return _hold(signal, "invalid_macro_event_symbols")
            if pair not in symbols and "*" not in symbols:
                continue
            start, end = _utc(event["starts_at"]), _utc(event["ends_at"])
            if end <= start:
                return _hold(signal, "invalid_macro_event_window")
            if not start <= now <= end:
                continue
            source_urls = event.get("source_urls", [])
            if not isinstance(source_urls, list) or not source_urls or any(
                not isinstance(link, str) or urlsplit(link).scheme != "https"
                or not urlsplit(link).hostname for link in source_urls
            ):
                return _hold(signal, "macro_event_needs_https_evidence")
            return _hold(signal, "reviewed_high_impact_event")
        return {**signal, "macro_guard": {"decision": "allowed", "reason": "no_active_reviewed_hold"}}
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return _hold(signal, "macro_report_not_verified")
