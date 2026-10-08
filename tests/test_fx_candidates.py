import math
import unittest
from unittest.mock import patch
from datetime import datetime,timedelta,timezone
from brobs.fx_candidates import reversion
from brobs.fx_optimize import evaluate
from brobs.fx_research import replay

class CandidateTests(unittest.TestCase):
    def test_extreme_prices_and_flat_series(self):
        self.assertEqual(reversion([1.1]*19+[1.0])[0],'buy')
        self.assertEqual(reversion([1.1]*19+[1.2])[0],'sell')
        self.assertEqual(reversion([1.1]*40)[0],'hold')
    def test_invalid_data_abstains(self):
        for closes in ([1.1]*19,[math.nan]*30,[0.0]*30,[math.inf]*30):
            self.assertEqual(reversion(closes)[0],'hold')
        with self.assertRaises(ValueError):reversion([1.1]*40,period=2)
    def test_callback_never_sees_execution_bar(self):
        rows=[dict(timestamp=datetime(2024,1,1,tzinfo=timezone.utc)+timedelta(hours=i),open=1+i*.0001,high=1.01+i*.0001,low=.99+i*.0001,close=1+i*.0001) for i in range(60)]
        seen=[]
        def signal(closes):seen.append(closes[-1]);return 'hold',[]
        replay(rows,30,signal_fn=signal)
        self.assertEqual(seen,[r['close'] for r in rows[29:59]])
    def test_candidate_selection_never_receives_later_bars(self):
        rows=[dict(timestamp=datetime(2024,1,1,tzinfo=timezone.utc)+timedelta(hours=i)) for i in range(600)]
        calls=[]
        def fake(data,start,**kwargs):
            calls.append((len(data),start))
            return dict(closed_trades=44,net_pnl=1,profit_factor=1.2,max_drawdown_pct=.2,win_rate_pct=70)
        with patch('brobs.fx_optimize.replay',side_effect=fake):r=evaluate(rows)
        self.assertEqual(calls[:12],[(420,252)]*12)
        self.assertEqual(calls[12],(600,420))
        self.assertIn('not a pristine holdout',r['caveat'])
    def test_no_eligible_candidate_fails_closed(self):
        rows=[dict(timestamp=datetime(2024,1,1,tzinfo=timezone.utc)) for _ in range(600)]
        bad=dict(closed_trades=3,net_pnl=-1,profit_factor=.2,max_drawdown_pct=.2,win_rate_pct=100)
        with patch('brobs.fx_optimize.replay',return_value=bad),self.assertRaises(ValueError):evaluate(rows)
