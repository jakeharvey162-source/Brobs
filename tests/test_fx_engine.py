import math
import os
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from brobs.fx import FXBook, FXConfig, statistics
from brobs.fx_runner import tick
from brobs.app import make_server
from brobs.oanda_practice import PracticeData

NOW=datetime(2026,10,8,12,tzinfo=timezone.utc)
def quote(bid=1.1,ask=1.1002,at=NOW):
    return {'EUR_USD':dict(bid=bid,ask=ask,timestamp=at.isoformat(),tradeable=True)}
def sig(action='buy',id='bar1'):return {'EUR_USD':dict(action=action,id=id)}

class EngineTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.path=os.path.join(self.folder.name,'fx.db')
        self.cfg=FXConfig(slippage_fraction=0)
        self.book=FXBook(self.path,self.cfg)
    def tearDown(self):self.folder.cleanup()
    def open(self,action='buy'):return self.book.process(quote(),sig(action),'open',NOW)
    def test_long_opens_at_ask_and_marks_at_bid(self):
        self.open();s=self.book.snapshot();p=s['positions']['EUR_USD']
        self.assertEqual(p['entry'],1.1002)
        self.assertAlmostEqual(s['equity'],10000+p['units']*(1.1-1.1002))
        self.assertGreater(s['free_margin'],0)
    def test_short_opens_at_bid_and_marks_at_ask(self):
        self.open('sell');s=self.book.snapshot();p=s['positions']['EUR_USD']
        self.assertLess(p['units'],0);self.assertEqual(p['entry'],1.1)
        self.assertAlmostEqual(s['unrealized_pnl'],p['units']*(1.1002-1.1))
    def test_duplicate_tick_is_atomic_across_workers(self):
        with ThreadPoolExecutor(max_workers=5) as pool:
            results=list(pool.map(lambda _:self.book.process(quote(),sig(),'same',NOW),range(12)))
        self.assertEqual(sum(r['status']=='paper' for r in results),1)
        self.assertEqual(len(self.book.snapshot()['events']),1)
    def test_same_signal_new_quote_does_not_reenter(self):
        self.open();self.book.process(quote(1.101,1.1012,NOW+timedelta(seconds=1)),sig(),'next',NOW+timedelta(seconds=1))
        self.assertEqual(len(self.book.snapshot()['positions']),1)
        self.assertEqual(len(self.book.snapshot()['events'][0]['fills']),0)
    def test_stop_runs_on_duplicate_signal(self):
        self.open();self.book.process(quote(1.08,1.0802,NOW+timedelta(seconds=1)),sig(),'stop',NOW+timedelta(seconds=1))
        s=self.book.snapshot();self.assertEqual(s['positions'],{})
        self.assertEqual(s['stats']['losses'],1);self.assertEqual(s['trades'][0]['reason'],'stop')
    def test_short_take_profit_and_realized_pnl(self):
        self.open('sell');s=self.book.snapshot();units=s['positions']['EUR_USD']['units']
        self.book.process(quote(1.08,1.0802,NOW+timedelta(seconds=1)),sig('sell'),'tp',NOW+timedelta(seconds=1))
        s=self.book.snapshot();self.assertAlmostEqual(s['balance']-10000,units*(1.0802-1.1))
        self.assertEqual(s['stats']['wins'],1)
    def test_commissions_are_charged_once_per_side(self):
        book=FXBook(os.path.join(self.folder.name,'fees.db'),FXConfig(slippage_fraction=0,commission_fraction=.001))
        book.process(quote(),sig(),'open',NOW);p=book.snapshot()['positions']['EUR_USD']
        book.process(quote(1.1001,1.1003,NOW+timedelta(seconds=1)),sig('sell','bar2'),'close',NOW+timedelta(seconds=1))
        s=book.snapshot();expected=p['units']*(1.1001-1.1002)-p['entry_fee']-p['units']*1.1001*.001
        self.assertAlmostEqual(s['balance']-10000,expected);self.assertAlmostEqual(s['stats']['net_pnl'],expected,places=3)
    def test_restart_preserves_position_and_signal(self):
        self.open();book=FXBook(self.path,self.cfg)
        self.assertEqual(book.snapshot()['positions'],self.book.snapshot()['positions'])
        self.assertEqual(book.process(quote(),sig(),'open',NOW)['status'],'duplicate_tick')
    def test_missing_mark_rolls_back(self):
        self.open()
        with self.assertRaises(ValueError):self.book.process({'GBP_USD':quote()['EUR_USD']},{},'bad',NOW)
        self.assertEqual(len(self.book.snapshot()['events']),1)
    def test_stale_future_and_nonfinite_quotes_rejected(self):
        for q in [quote(at=NOW-timedelta(minutes=3)),quote(at=NOW+timedelta(minutes=3)),quote(bid=math.nan),quote(ask=math.inf),quote(bid=1.2,ask=1.1)]:
            with self.subTest(q=q),self.assertRaises(ValueError):self.book.process(q,sig(),'bad',NOW)
        self.assertEqual(self.book.snapshot()['positions'],{})
    def test_non_usd_quote_rejected(self):
        with self.assertRaises(ValueError):self.book.process({'USD_JPY':quote()['EUR_USD']},{},'bad',NOW)
    def test_wide_spread_blocks_new_entry(self):
        self.book.process(quote(1.1,1.11),sig(),'wide',NOW)
        self.assertEqual(self.book.snapshot()['positions'],{})
    def test_pause_blocks_entries_but_keeps_stops(self):
        self.open();self.book.pause()
        self.book.process(quote(1.08,1.0802,NOW+timedelta(seconds=1)),sig(),'stop',NOW+timedelta(seconds=1))
        self.assertEqual(self.book.snapshot()['positions'],{})
        self.book.process(quote(at=NOW+timedelta(seconds=2)),sig('buy','bar3'),'blocked',NOW+timedelta(seconds=2))
        self.assertEqual(self.book.snapshot()['positions'],{})
    def test_loss_limit_halts_and_closes(self):
        book=FXBook(os.path.join(self.folder.name,'risk.db'),FXConfig(slippage_fraction=0,daily_loss_fraction=.001))
        book.process(quote(),sig(),'open',NOW)
        book.process(quote(1.094,1.0942,NOW+timedelta(seconds=1)),sig(),'loss',NOW+timedelta(seconds=1))
        self.assertEqual(book.snapshot()['halted_reason'],'daily_loss');self.assertEqual(book.snapshot()['positions'],{})
    def test_daily_halt_resets_next_utc_day(self):
        book=FXBook(os.path.join(self.folder.name,'day.db'),FXConfig(slippage_fraction=0,daily_loss_fraction=.001))
        book.process(quote(),sig(),'open',NOW)
        book.process(quote(1.094,1.0942,NOW+timedelta(seconds=1)),sig(),'loss',NOW+timedelta(seconds=1))
        tomorrow=NOW+timedelta(days=1)
        book.process(quote(at=tomorrow),sig('buy','nextday'),'day',tomorrow)
        self.assertIsNone(book.snapshot()['halted_reason'])
    def test_out_of_order_tick_rejected(self):
        self.open()
        with self.assertRaises(ValueError):self.book.process(quote(at=NOW-timedelta(seconds=1)),{},'old',NOW-timedelta(seconds=1))
    def test_changed_config_rejected_on_restart(self):
        with self.assertRaises(ValueError):FXBook(self.path,FXConfig(capital=20000))
    def test_invalid_configuration(self):
        for kwargs in [{'capital':math.nan},{'risk_fraction':.1},{'max_notional_fraction':1},{'stop_fraction':0}]:
            with self.assertRaises(ValueError):FXConfig(**kwargs)
    def test_empty_sample_does_not_invent_win_rate(self):
        self.assertIsNone(statistics([])['win_rate_pct'])
        s=statistics([{'pnl':10},{'pnl':-5},{'pnl':0}])
        self.assertEqual(s['profit_factor'],2);self.assertEqual(s['wins'],1)
        self.assertEqual(s['evidence'],'insufficient_sample')
    def test_account_pricing_adapter(self):
        def fake(path):
            self.assertIn('/pricing?',path)
            return {'prices':[{'instrument':'EUR_USD','bids':[{'price':'1.1'}],'asks':[{'price':'1.1002'}],'time':NOW.isoformat(),'status':'tradeable'}]}
        q=PracticeData('secret','account-12345',fake).quotes()
        self.assertEqual(q['EUR_USD']['ask'],1.1002)
    def test_poll_end_to_end_and_repeat(self):
        class Data:
            def account_summary(self):return {'currency':'USD'}
            def candles(self,**kwargs):return [{'timestamp':NOW-timedelta(hours=60-i),'close':1.08+i*.0001} for i in range(60)]
            def quotes(self,pairs):return quote()
        result=tick(Data(),self.book,now=NOW)
        self.assertEqual(result['status'],'paper');self.assertEqual(len(self.book.snapshot()['positions']),1)
        self.assertEqual(tick(Data(),self.book,now=NOW)['status'],'duplicate_tick')
    def test_wrong_account_currency_blocks_poll(self):
        class Data:
            def account_summary(self):return {'currency':'ZAR'}
        with self.assertRaises(ValueError):tick(Data(),self.book,now=NOW)
    def test_dashboard_http_and_no_mutation(self):
        self.open();server=make_server(self.path,0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base='http://127.0.0.1:'+str(server.server_port)
        try:
            import json
            with urlopen(base+'/api/state') as r:
                state=json.load(r);self.assertIn('EUR_USD',state['positions']);self.assertEqual(r.headers['Cache-Control'],'no-store')
            with urlopen(base) as r:self.assertIn(b'Observed win rate',r.read())
            with self.assertRaises(HTTPError):urlopen(Request(base+'/api/state',data=b'{}',method='POST'))
            with self.assertRaises(HTTPError):urlopen(base+'/not-real')
        finally:server.shutdown();server.server_close();thread.join()
