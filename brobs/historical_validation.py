"""Deterministic validation for local historical OHLCV bars.

Timestamps denote bar opens. Completeness needs an explicit ``as_of`` and bar
interval: the wall clock is deliberately never used. Session gap checks use
named, limited calendars; they do not certify a vendor's data or exchange rules.
"""
from collections.abc import Mapping
from datetime import date, datetime, timedelta, timezone
from math import isfinite
from zoneinfo import ZoneInfo

UTC = timezone.utc
FIELDS = ("open", "high", "low", "close", "volume")
MAX_GAP_STEPS = 1_000_000


def timestamp(value, *, allow_naive_utc=False):
    """Normalize an aware ISO timestamp; naive UTC is an explicit legacy opt-in."""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("Invalid historical timestamp") from exc
    if not isinstance(value, datetime):
        raise ValueError("Historical timestamp must be an aware datetime or ISO string")
    if value.tzinfo is None or value.utcoffset() is None:
        if not allow_naive_utc:
            raise ValueError("Historical timestamp requires an explicit timezone")
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def interval_seconds(interval):
    value = interval.total_seconds() if isinstance(interval, timedelta) else interval
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not isfinite(value) or value < 1 or int(value) != value):
        raise ValueError("Historical interval must be positive whole seconds")
    return int(value)


def _nth_weekday(year, month, weekday, occurrence):
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (occurrence - 1))


def _observed(day):
    return day - timedelta(days=1) if day.weekday() == 5 else day + timedelta(days=1) if day.weekday() == 6 else day


def _easter(year):
    # Gregorian computus; Good Friday is the recurring US stock-market closure.
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    return date(year, (h + l - 7 * m + 114) // 31, (h + l - 7 * m + 114) % 31 + 1)


def _stock_holidays(year):
    holidays = {
        _nth_weekday(year, 2, 0, 3),
        _easter(year) - timedelta(days=2),
        date(year, 5, 31) - timedelta(days=date(year, 5, 31).weekday()),
        _observed(date(year, 7, 4)),
        _nth_weekday(year, 9, 0, 1),
        _nth_weekday(year, 11, 3, 4),
        _observed(date(year, 12, 25)),
    }
    # NYSE does not move a Saturday New Year's Day to the preceding Friday.
    new_year = date(year, 1, 1)
    if new_year.weekday() != 5:
        holidays.add(_observed(new_year))
    if year >= 1998:
        holidays.add(_nth_weekday(year, 1, 0, 3))  # NYSE began observing MLK Day in 1998.
    if year >= 2022:
        holidays.add(_observed(date(year, 6, 19)))
    return holidays


def _calendar(market, seconds):
    if market is None or market == "crypto":
        return "continuous_24_7", "No closed sessions assumed"
    if market == "forex":
        return "forex_new_york_17_weekend", "Only New York Friday 17:00 to Sunday 17:00 weekend closures; provider holidays are not certified"
    if market == "stock" and seconds == 86400:
        return "us_stock_daily_recurring_holidays", "Weekends and recurring US stock holidays only; exceptional exchange closures and corporate actions are not certified"
    raise ValueError("Unsupported historical session calendar; stock gap checks require daily bars")


def audit_gaps(rows, interval, market=None):
    """Count missing scheduled bars, retaining only a bounded diagnostic sample.

    The input should already have passed ``validate_rows`` without an interval.
    No missing bar is interpolated, forward-filled or silently dropped.
    """
    seconds = interval_seconds(interval)
    calendar, limitation = _calendar(market, seconds)
    expected_closures = missing_count = 0
    missing = []
    holidays = {}
    stamps = [timestamp(row["timestamp"]) for row in rows]
    stock_zone = None
    if market == "stock":
        # Daily date labels and actual exchange opens have different grids.
        # UTC midnight labels stay on UTC dates; NY opens stay at 09:30 local
        # time across DST, so a weekend can contain 71 or 73 elapsed UTC hours.
        if all((stamp.hour, stamp.minute, stamp.second, stamp.microsecond) == (0, 0, 0, 0)
               for stamp in stamps):
            stock_zone = UTC
        else:
            stock_zone = ZoneInfo("America/New_York")
            local = [stamp.astimezone(stock_zone) for stamp in stamps]
            if not all((stamp.hour, stamp.minute, stamp.second, stamp.microsecond) == (9, 30, 0, 0)
                       for stamp in local):
                raise ValueError("Unsupported daily stock timestamp convention: use UTC-midnight date labels or New York 09:30 session opens consistently")

    def closed_session(when):
        if market == "forex":
            local = when.astimezone(ZoneInfo("America/New_York"))
            return (local.weekday() == 5 or (local.weekday() == 4 and local.hour >= 17)
                    or (local.weekday() == 6 and local.hour < 17))
        if market == "stock":
            day = when.astimezone(stock_zone).date()
            if day.year not in holidays:
                holidays[day.year] = _stock_holidays(day.year)
            return day.weekday() >= 5 or day in holidays[day.year]
        return False

    unexpected_count = 0
    unexpected = []
    for stamp in stamps:
        if closed_session(stamp):
            unexpected_count += 1
            if len(unexpected) < 20:
                unexpected.append(stamp.isoformat())
    total_gap_steps = 0
    for earlier, later in zip(rows, rows[1:]):
        start, end = timestamp(earlier["timestamp"]), timestamp(later["timestamp"])
        elapsed = (end - start).total_seconds()
        if elapsed <= 0:
            raise ValueError("Historical timestamps must be ordered and aligned to the interval")
        if stock_zone is not None:
            grid_start = start.astimezone(stock_zone)
            steps = (end.astimezone(stock_zone).date() - grid_start.date()).days - 1
            if steps < 0:
                raise ValueError("Daily stock bars require distinct ordered session dates")
        else:
            if elapsed % seconds:
                raise ValueError("Historical timestamps must be ordered and aligned to the interval")
            steps = int(elapsed // seconds) - 1
        total_gap_steps += steps
        if steps > MAX_GAP_STEPS or total_gap_steps > MAX_GAP_STEPS:
            raise ValueError("Historical gap exceeds bounded calendar audit limit")
        if calendar == "continuous_24_7":
            missing_count += steps
            for i in range(min(steps, 20 - len(missing))):
                missing.append((start + timedelta(seconds=seconds * (i + 1))).isoformat())
            continue
        for i in range(1, steps + 1):
            when = ((grid_start + timedelta(days=i)).astimezone(UTC)
                    if stock_zone is not None else start + timedelta(seconds=seconds * i))
            if closed_session(when):
                expected_closures += 1
            else:
                missing_count += 1
                if len(missing) < 20:
                    missing.append(when.isoformat())
    return dict(interval_seconds=seconds, calendar=calendar,
                expected_closures=expected_closures, missing_count=missing_count,
                missing_timestamps_sample=missing,
                unexpected_closed_session_count=unexpected_count,
                unexpected_closed_session_timestamps_sample=unexpected,
                calendar_limitation=limitation)


def validate_rows(rows, *, min_rows=30, interval=None, market=None, as_of=None,
                  allow_naive_utc=False, require_volume=True):
    """Return independent, validated UTC bars; never reorder or repair input.

    ``require_volume=False`` preserves the OHLC-only replay API. Any supplied
    volume is still checked; missing values are never invented. CSV/report paths
    require complete OHLCV by default.
    """
    if isinstance(min_rows, bool) or not isinstance(min_rows, int) or min_rows < 1:
        raise ValueError("Invalid minimum historical sample")
    if not isinstance(rows, (list, tuple)) or len(rows) < min_rows:
        raise ValueError(f"At least {min_rows} observations required")
    normalized = []
    required = FIELDS if require_volume else FIELDS[:-1]
    for item in rows:
        if not isinstance(item, Mapping) or "timestamp" not in item or any(k not in item for k in required):
            raise ValueError("Historical rows require timestamp and complete OHLCV fields")
        row = dict(item)
        row["timestamp"] = timestamp(item["timestamp"], allow_naive_utc=allow_naive_utc)
        for field in FIELDS:
            if field not in item:
                continue
            value = item[field]
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not isfinite(value) or value < 0 or (field != "volume" and value == 0)):
                raise ValueError("Invalid historical OHLCV value")
        if row["low"] > min(row["open"], row["close"]) or row["high"] < max(row["open"], row["close"]):
            raise ValueError("Inconsistent historical price range")
        if normalized and row["timestamp"] <= normalized[-1]["timestamp"]:
            raise ValueError("Duplicate or out-of-order historical timestamps")
        normalized.append(row)
    if as_of is not None and interval is None:
        raise ValueError("An explicit bar interval is required with as_of")
    if interval is not None:
        seconds = interval_seconds(interval)
        if as_of is not None and normalized[-1]["timestamp"] + timedelta(seconds=seconds) > timestamp(as_of):
            raise ValueError("Incomplete current or future historical bar")
        gap_report = audit_gaps(normalized, seconds, market)
        if gap_report["unexpected_closed_session_count"]:
            raise ValueError(f"Unexpected {gap_report['unexpected_closed_session_count']} historical candles in closed market sessions")
        if gap_report["missing_count"]:
            raise ValueError(f"Missing {gap_report['missing_count']} scheduled historical candles")
    return normalized
