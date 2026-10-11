"""Read-only operational audit for BROBS paper trading, inspired by robust bot monitoring.

Do not use this report as a trade signal or evidence of investment profit.
"""
from __future__ import annotations
import argparse
import json
import math
from datetime import datetime, timezone

STALE_AFTER_SECONDS = 120
MIN_EVIDENCE_TRADES = 100

def _age(value, now):
    if not value:
        return None
    try:
        t = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if t.tzinfo is None:
            return None
        diff = (now-t.astimezone(timezone.utc)).total_seconds()
        if not math.isfinite(diff) or diff < -30:
            return None
        return max(0, round(diff))
    except (ValueError, OverflowError, TypeError):
        return None

def report(snapshot, now=None):
    """Analyze an existing SQLite snapshot; never poll a broker or submit orders."""
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Audit current time requires a timezone")
    if not isinstance(snapshot, dict):
        raise ValueError("Expected a paper account snapshot")
    stats = snapshot.get("stats") or {}
    health = snapshot.get("health") or {}
    trades = int(stats.get("closed_trades") or 0)
    positions = snapshot.get("positions") or {}
    max_drawdown = float(snapshot.get("max_drawdown") or 0)
    equity = float(snapshot.get("equity") or 0)
    if not math.isfinite(equity) or not math.isfinite(max_drawdown):
        raise ValueError("Non-finite ledger metrics")
    last_quote_age = _age(snapshot.get("last_tick"), now)
    health_age = _age(health.get("timestamp"), now)
    runner_current = (health.get("status") == "ok" and
                      last_quote_age is not None and last_quote_age <= STALE_AFTER_SECONDS and
                      health_age is not None and health_age <= STALE_AFTER_SECONDS)
    reasons = []
    if not runner_current:
        reasons.append("Runner or prices are stale/unverified; do not rely on saved marks for live exposure.")
    if snapshot.get("paused"):
        reasons.append("New entries paused by operator.")
    if snapshot.get("halted_reason"):
        reasons.append("Ledger halted: " + str(snapshot["halted_reason"])[:80])
    if positions and not runner_current:
        reasons.append("Open paper positions are not receiving verified current stop checks.")
    if trades < MIN_EVIDENCE_TRADES:
        reasons.append("Sample is too small to claim a durable trading edge.")
    if trades >= MIN_EVIDENCE_TRADES:
        reasons.append("Historical trade counts alone do not establish forward profitability.")
    state = "HALTED" if snapshot.get("halted_reason") else "PAUSED" if snapshot.get("paused") else ("ACTIVE_PAPER" if runner_current else "STALE")
    return {
        "engine": "BROBS",
        "execution": "LOCAL_PAPER_ONLY",
        "real_money_orders_enabled": False,
        "checked_at": now.astimezone(timezone.utc).isoformat(),
        "state": state,
        "runner_current": runner_current,
        "last_tick_age_seconds": last_quote_age,
        "health_age_seconds": health_age,
        "open_positions": len(positions),
        "closed_trades": trades,
        "observed_win_rate_pct": stats.get("win_rate_pct"),
        "observed_profit_factor": stats.get("profit_factor"),
        "max_drawdown_pct": round(max_drawdown*100, 2),
        "equity_snapshot": round(equity, 4),
        "quote_currency": str(snapshot.get("quote_currency") or "USD"),
        "confidence": "INSUFFICIENT_SAMPLE" if trades < MIN_EVIDENCE_TRADES else "BACKTEST_OR_PAPER_ONLY",
        "risks": reasons,
    }

def main(argv=None):
    p = argparse.ArgumentParser(description="BROBS local paper engine audit (no broker orders)")
    p.add_argument("--db", default="brobs_fx.db")
    p.add_argument("--market", choices=("forex", "crypto", "stock"))
    args = p.parse_args(argv)
    from .app import open_book
    data = report(open_book(args.db, args.market).snapshot())
    print(json.dumps(data, indent=2, allow_nan=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
