"""Load user-provided historical OHLCV data from a CSV file."""
import csv
from datetime import datetime, timezone
from math import isfinite

def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as source:
        for item in csv.DictReader(source):
            timestamp = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            row = {"timestamp": timestamp}
            for field in ("open", "high", "low", "close", "volume"):
                value = float(item[field])
                if not isfinite(value) or value < 0:
                    raise ValueError("Invalid market data")
                row[field] = value
            if min(row["open"], row["high"], row["low"], row["close"]) <= 0:
                raise ValueError("Invalid prices")
            if row["low"] > min(row["open"], row["close"]) or row["high"] < max(row["open"], row["close"]):
                raise ValueError("Inconsistent price range")
            if rows and timestamp <= rows[-1]["timestamp"]:
                raise ValueError("Out-of-order timestamps")
            rows.append(row)
    if len(rows) < 30:
        raise ValueError("At least 30 observations required")
    return rows
