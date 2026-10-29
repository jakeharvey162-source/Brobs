"""Load user-provided historical OHLCV data from a CSV file."""
import csv
from .historical_validation import FIELDS, validate_rows

def load_csv(path, **validation):
    """Read OHLCV with explicit timezones (``allow_naive_utc=True`` opts in to legacy UTC)."""
    rows = []
    with open(path, newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or not {"timestamp", *FIELDS}.issubset(reader.fieldnames):
            raise ValueError("Historical CSV requires timestamp and OHLCV columns")
        if len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("Historical CSV has duplicate columns")
        for item in reader:
            if None in item:
                raise ValueError("Historical CSV row has unexpected extra columns")
            try:
                row = dict(timestamp=item["timestamp"], **{field: float(item[field]) for field in FIELDS})
            except (TypeError, ValueError) as exc:
                raise ValueError("Malformed historical OHLCV row") from exc
            rows.append(row)
    return validate_rows(rows, **validation)
