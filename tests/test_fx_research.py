import math
import unittest
from datetime import datetime,timedelta,timezone
from brobs.fx_research import replay,load_forex_csv
from brobs.fx_signals import decide
from brobs.ml_agent import predict

class ReplayTests(unittest.TestCase):
    def rows(self,n=100):
        return [dict(timestamp=datetime(2024,1,1,tzinfo=timezone.utc)+timedelta(hours=i),
            open=1.1+i*.0001,high=1.101+i*.0001,low=1.099+i*.0001,close=1.1005+i*.0001,volume=10) for i in range(n)]
    def test_replay_includes_liquidation_and_valid_statistics(self):
        r=replay(self.rows(),70)
        self.assertGreater(r['closed_trades'],0)
        self.assertAlmostEqual(r['ending_equity']-10000,r['net_pnl'],places=3)
        self.assertEqual(r['evidence'],'insufficient_sample')
    def test_signal_receives_only_bars_before_fill(self):
        from unittest.mock import patch
        rows=self.rows(); calls=[]
        def inspect(closes):
            calls.append(list(closes))
            return 'hold', []
        with patch('brobs.fx_research.decide',side_effect=inspect):replay(rows,70)
        self.assertEqual(len(calls),30)
        self.assertEqual(calls[0][-1],rows[69]['close'])
        self.assertNotIn(rows[70]['close'],calls[0])
        self.assertEqual(calls[-1][-1],rows[98]['close'])
    def test_flat_data_does_not_invent_trades(self):
        rows=self.rows()
        for r in rows:r.update(open=1.1,high=1.1,low=1.1,close=1.1)
        self.assertIsNone(replay(rows,70)['win_rate_pct'])
    def test_optional_ml_rejects_invalid_data(self):
        self.assertEqual(predict([math.nan]*200)['action'],'unknown')
        self.assertEqual(predict([1.1]*100)['action'],'unknown')
    def test_public_dataset_validation(self):
        rows=load_forex_csv('research/data/EURUSD_1h.csv')
        self.assertEqual(len(rows),3162)
        self.assertLess(rows[0]['timestamp'],rows[-1]['timestamp'])
