import unittest
from datetime import datetime,timedelta,timezone
from brobs.market_signals import signal
from brobs.winrate_lab import sample_check,RSI2Cache,candidates

class WinRateTests(unittest.TestCase):
    def test_70_observed_is_not_70_supported(self):
        result=sample_check(dict(closed_trades=100,wins=70))
        self.assertFalse(result['historical_count_gate'])
        self.assertFalse(result['verified_future_probability'])
        self.assertLess(result['wilson_95pct_interval'][0],70)
    def test_tiny_perfect_sample_does_not_pass(self):
        self.assertFalse(sample_check(dict(closed_trades=5,wins=5))['historical_count_gate'])
        self.assertIsNone(sample_check(dict(closed_trades=0,wins=0))['observed_pct'])
    def test_large_sample_still_not_future_probability(self):
        result=sample_check(dict(closed_trades=1000,wins=800))
        self.assertTrue(result['historical_count_gate'])
        self.assertFalse(result['verified_future_probability'])
    def test_invalid_counts_rejected(self):
        for n,w in [(100,101),(-1,0),(True,1),(100,True),(100.,70)]:
            with self.assertRaises(ValueError):sample_check(dict(closed_trades=n,wins=w))
    def test_cache_matches_runner_and_cannot_read_future(self):
        now=datetime(2025,1,1,tzinfo=timezone.utc)
        rows=[dict(timestamp=now+timedelta(hours=i),close=100+i*.02+((i%19)-9)*.3) for i in range(540)]
        cache=RSI2Cache(rows)
        for end in (100,220,510,539):
            history=rows[max(0,end-500):end]
            for side in (-1,0,1):
                for threshold in (5,10,20,35):
                    for short in (True,False):
                        self.assertEqual(cache.callback(threshold,short)(history,side)[0],signal(history,'rsi2_reversion',side,threshold,short)[0])
        prefix=RSI2Cache(rows[:220]);self.assertEqual(prefix.values[rows[219]['timestamp']],cache.values[rows[219]['timestamp']])
        rows[-1]['close']=99999
        self.assertEqual(prefix.values[rows[219]['timestamp']],RSI2Cache(rows).values[rows[219]['timestamp']])
    def test_candidate_manifest_is_bounded_and_risk_limited(self):
        for market in ('forex','stock','crypto'):
            profiles=candidates(market);self.assertEqual(len(profiles),16)
            self.assertEqual(len({tuple(p.values()) for p in profiles}),16)
            self.assertTrue(all(p['reward_risk']>=1 for p in profiles))
    def test_reused_evaluation_cannot_become_verified_or_authorize_entries(self):
        from unittest.mock import patch
        from brobs.winrate_lab import evaluate
        now=datetime(2025,1,1,tzinfo=timezone.utc)
        rows=[dict(timestamp=now+timedelta(hours=i)) for i in range(600)]
        metrics=dict(closed_trades=1000,wins=800,net_pnl=100,profit_factor=2,return_pct=1)
        with patch('brobs.winrate_lab.RSI2Cache'),patch('brobs.winrate_lab.run',return_value=metrics):
            report=evaluate(rows,'crypto','BTC_USDT')
        self.assertTrue(report['exploratory_target_gates_pass'])
        self.assertFalse(report['historical_acceptance'])
        self.assertFalse(report['verified_70_percent'])
        self.assertFalse(report['auto_promotion'])
