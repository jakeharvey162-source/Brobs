import importlib.util,unittest
from brobs.freqtrade_bridge import stake_cap
from brobs.fx_signals import decide

class StakeTests(unittest.TestCase):
    def test_exchange_minimum_does_not_force_oversized_trade(self):
        self.assertEqual(stake_cap(10,60000,10,5,10),0)
        self.assertEqual(stake_cap(10,60000,10,1,10),2)
    def test_invalid_and_nonfinite_stakes_abstain(self):
        for x in (float('nan'),float('inf'),-1,True):self.assertEqual(stake_cap(x,60000,10,1,10),0)

@unittest.skipUnless(importlib.util.find_spec('pandas'),'Optional pandas not installed')
class SignalParityTests(unittest.TestCase):
    def test_prefix_signals_match_python_without_future_data(self):
        import pandas as pd
        from brobs.freqtrade_bridge import columns
        prices=[100+i*.03+((i%17)-8)*.015 for i in range(260)]
        frame=pd.DataFrame(dict(close=prices,volume=[1]*len(prices)));out=columns(frame)
        for i in range(30,len(prices)):
            expected=decide(prices[max(0,i-199):i+1])[0]
            actual='buy' if out.loc[i,'brobs_buy'] else 'sell' if out.loc[i,'brobs_sell'] else 'hold'
            self.assertEqual(expected,actual)
        pd.testing.assert_frame_equal(out.iloc[:200],columns(frame.iloc[:200]))
        frame.loc[250,'close']=99999
        pd.testing.assert_frame_equal(out.iloc[:200],columns(frame).iloc[:200])
    def test_invalid_close_blocks_entry_and_input_is_not_mutated(self):
        import pandas as pd
        from brobs.freqtrade_bridge import columns
        frame=pd.DataFrame(dict(close=[100+i*.1 for i in range(60)],volume=[1]*60));frame.loc[50,'close']=float('nan')
        before=frame.copy();out=columns(frame)
        self.assertFalse(out.loc[59,'brobs_buy']);pd.testing.assert_frame_equal(before,frame)
