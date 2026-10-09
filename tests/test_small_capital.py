import json,subprocess,sys,tempfile,unittest
from pathlib import Path
from dataclasses import replace
from datetime import datetime,timezone
from brobs.market_book import StockBook,CryptoBook,default_config

class SmallCapitalTests(unittest.TestCase):
    def test_market_cli_persists_ten_unit_paper_balance(self):
        with tempfile.TemporaryDirectory() as folder:
            for market in ('stock','crypto'):
                path=str(Path(folder)/(market+'.db'))
                result=subprocess.run([sys.executable,'-m','brobs.market_runner','--market',market,'--capital','10','--demo','--once','--db',path],capture_output=True,text=True,check=True)
                equity=json.loads(result.stdout)['equity']
                self.assertGreater(equity,0);self.assertLessEqual(equity,10) # A demo entry incurs costs.
                cls=StockBook if market=='stock' else CryptoBook
                cfg=replace(default_config(market),capital=10)
                self.assertEqual(cls(path,cfg).snapshot()['initial_equity'],10)
                with self.assertRaises(ValueError):cls(path,default_config(market))
    def test_tiny_stock_account_records_reason_without_fake_fill(self):
        with tempfile.TemporaryDirectory() as folder:
            b=StockBook(str(Path(folder)/'stock.db'),replace(default_config('stock'),capital=10))
            now=datetime(2026,10,9,tzinfo=timezone.utc)
            q={'AAPL':dict(bid=200,ask=200,timestamp=now.isoformat(),tradeable=True)}
            result=b.process(q,{'AAPL':dict(id='small',action='buy')},'tick',now)
            self.assertEqual(result['fills'],[])
            self.assertEqual(result['entry_vetoes'][0]['reason'],'insufficient_units')
            state=b.snapshot();self.assertEqual(state['equity'],10);self.assertEqual(state['positions'],{})
            self.assertEqual(state['events'][-1]['entry_vetoes'],result['entry_vetoes'])
    def test_tiny_crypto_position_remains_under_notional_and_cash_caps(self):
        with tempfile.TemporaryDirectory() as folder:
            b=CryptoBook(str(Path(folder)/'crypto.db'),replace(default_config('crypto'),capital=10))
            now=datetime(2026,10,9,tzinfo=timezone.utc)
            q={'BTC_USDT':dict(bid=60000,ask=60000,timestamp=now.isoformat(),tradeable=True)}
            b.process(q,{'BTC_USDT':dict(id='small',action='buy')},'tick',now)
            state=b.snapshot();p=state['positions']['BTC_USDT']
            self.assertLessEqual(p['units']*p['entry'],2)
            self.assertGreaterEqual(state['free_margin'],0)
