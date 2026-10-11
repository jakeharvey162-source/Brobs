import json
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from brobs.operational_audit import report
from brobs.fx import FXBook, FXConfig

NOW = datetime(2026, 10, 11, 17, tzinfo=timezone.utc)
def base(**overrides):
    val = dict(stats={"closed_trades":4, "win_rate_pct":75, "profit_factor":3},
        health={"status":"ok","timestamp":NOW.isoformat()},
        last_tick=NOW.isoformat(), positions={}, paused=False,
        halted_reason=None, max_drawdown=.015, equity=10040,
        quote_currency="USD")
    val.update(overrides)
    return val

class OperationalAuditTests(unittest.TestCase):
    def test_active_paper_discloses_limited_evidence(self):
        result = report(base(), NOW)
        self.assertEqual(result["state"], "ACTIVE_PAPER")
        self.assertEqual(result["confidence"], "INSUFFICIENT_SAMPLE")
        self.assertFalse(result["real_money_orders_enabled"])
        self.assertEqual(result["observed_win_rate_pct"],75)
    def test_stale_open_position_warns_stop_checks_not_live(self):
        prior=(NOW-timedelta(minutes=6)).isoformat()
        result=report(base(last_tick=prior,positions={"EUR_USD":{"units":5}}),NOW)
        self.assertEqual(result["state"],"STALE")
        self.assertFalse(result["runner_current"])
        self.assertTrue(any("stop checks" in x for x in result["risks"]))
    def test_halt_is_never_presented_as_tradable(self):
        result=report(base(halted_reason="max_drawdown"), NOW)
        self.assertEqual(result["state"],"HALTED")
    def test_paused_state(self):
        self.assertEqual(report(base(paused=True), NOW)["state"],"PAUSED")
    def test_future_and_invalid_timestamp_not_current(self):
        for timevalue in ("nonsense",None,(NOW+timedelta(minutes=5)).isoformat()):
            with self.subTest(timevalue=timevalue):
                self.assertFalse(report(base(last_tick=timevalue),NOW)["runner_current"])
    def test_read_only_on_real_local_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"paper.db"
            book=FXBook(str(path),FXConfig())
            before=path.read_bytes()
            result=report(book.snapshot(),NOW)
            self.assertEqual(result["execution"],"LOCAL_PAPER_ONLY")
            self.assertEqual(path.read_bytes(),before)
    def test_nonfinite_values_rejected(self):
        with self.assertRaises(ValueError):
            report(base(equity=float("nan")),NOW)

if __name__=="__main__":
    unittest.main()
