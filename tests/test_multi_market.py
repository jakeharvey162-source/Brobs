import io
import json
import math
import os
import tempfile
import unittest
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timedelta,timezone
from urllib.request import urlopen
import threading
from brobs.fx import FXBook,FXConfig
from brobs.market_book import StockBook,CryptoBook,default_config
from brobs.market_signals import rsi,signal
from brobs.market_runner import tick,DemoData
from brobs.market_data import AlpacaData,BinanceData,validate_bars
from brobs.public_data import normalize_archive,download
from brobs.app import make_server,open_book

NOW=datetime(2026,9,1,12,tzinfo=timezone.utc)
def quotes(symbol,price=100,at=NOW):return {symbol:dict(bid=price,ask=price,timestamp=at.isoformat(),tradeable=True)}
def decision(symbol,action='buy',ident='bar1'):return {symbol:dict(id=ident,action=action)}

class MarketAccountingTests(unittest.TestCase):
    def setUp(self):self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
    def path(self,name='book.db'):return os.path.join(self.folder.name,name)
    def test_stock_sell_flat_never_shorts(self):
        b=StockBook(self.path(),default_config('stock'));b.process(quotes('AAPL'),decision('AAPL','sell'),'event',NOW)
        self.assertEqual(b.snapshot()['positions'],{})
    def test_stock_units_are_whole_and_unleveraged(self):
        b=StockBook(self.path(),default_config('stock'));b.process(quotes('AAPL',123),decision('AAPL'),'event',NOW)
        s=b.snapshot();self.assertEqual(s['positions']['AAPL']['units'],int(s['positions']['AAPL']['units']))
        self.assertGreaterEqual(s['free_margin'],0);self.assertLessEqual(s['margin_used'],2000)
    def test_crypto_fractional_units_and_fees_reconcile(self):
        cfg=default_config('crypto');b=CryptoBook(self.path(),cfg)
        b.process(quotes('BTC_USDT',60000),decision('BTC_USDT'),'open',NOW)
        p=b.snapshot()['positions']['BTC_USDT'];self.assertGreater(p['units'],0);self.assertLess(p['units'],1)
        at=NOW+timedelta(seconds=1);b.process(quotes('BTC_USDT',60100,at),decision('BTC_USDT','close','bar2'),'close',at)
        s=b.snapshot();self.assertAlmostEqual(s['balance']-10000,s['stats']['net_pnl'],places=3)
        self.assertEqual(s['quote_currency'],'USDT');self.assertEqual(s['stats']['closed_trades'],1)
        self.assertEqual(CryptoBook(self.path(),cfg).snapshot()['trades'],s['trades'])
    def test_profiles_are_isolated_and_unsupported_instruments_rejected(self):
        b=StockBook(self.path(),default_config('stock'))
        with self.assertRaises(ValueError):CryptoBook(self.path(),default_config('stock'))
        with self.assertRaises(ValueError):FXBook(self.path(),default_config('stock'))
        with self.assertRaises(ValueError):b.process(quotes('BTC_USDT'),decision('BTC_USDT'),'wrong',NOW)
    def test_close_flat_does_not_open_or_reverse(self):
        b=FXBook(self.path());b.process(quotes('EUR_USD',1.1),decision('EUR_USD','close'),'flat',NOW)
        self.assertEqual(b.snapshot()['positions'],{})
    def test_duplicate_concurrent_crypto_event_only_opens_once(self):
        b=CryptoBook(self.path(),default_config('crypto'))
        with ThreadPoolExecutor(max_workers=4) as pool:
            outcomes=list(pool.map(lambda _:b.process(quotes('BTC_USDT',60000),decision('BTC_USDT'),'same',NOW),range(8)))
        self.assertEqual(sum(bool(r['fills']) for r in outcomes),1)
    def test_pause_still_handles_crypto_stop(self):
        b=CryptoBook(self.path(),default_config('crypto'));b.process(quotes('BTC_USDT',60000),decision('BTC_USDT'),'open',NOW);b.pause()
        at=NOW+timedelta(seconds=1);b.process(quotes('BTC_USDT',57000,at),{},'stop',at)
        self.assertEqual(b.snapshot()['positions'],{});self.assertEqual(b.snapshot()['stats']['losses'],1)
    def test_auto_detect_crypto_dashboard_and_currency(self):
        b=CryptoBook(self.path(),default_config('crypto'));b.process(quotes('BTC_USDT',60000),decision('BTC_USDT'),'open',NOW)
        self.assertIsInstance(open_book(self.path()),CryptoBook)
        server=make_server(self.path(),0);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with urlopen('http://127.0.0.1:'+str(server.server_port)+'/api/state') as r:s=json.load(r)
            self.assertEqual(s['quote_currency'],'USDT');self.assertIn('BTC_USDT',s['positions'])
        finally:server.shutdown();server.server_close();thread.join()

class MarketFeedTests(unittest.TestCase):
    def test_incomplete_crypto_candle_excluded(self):
        stamp=int((NOW-timedelta(hours=1)).timestamp()*1000)
        def transport(path):return [[stamp,'100','101','99','100','1',stamp+3599999],[stamp+3600000,'100','101','99','100','1',stamp+7199999]]
        rows=BinanceData(transport).candles('BTC_USDT',NOW);self.assertEqual(len(rows),1)
    def test_crypto_snapshot_uses_prior_server_time(self):
        stamp=int(NOW.timestamp()*1000)
        def transport(path):return {'serverTime':stamp} if path.endswith('/time') else dict(symbol='BTCUSDT',bidPrice='100',askPrice='101',bidQty='1',askQty='2')
        q=BinanceData(transport).quotes(['BTC_USDT']);self.assertEqual(q['BTC_USDT']['timestamp'],NOW.isoformat())
    def test_stock_pages_fail_closed_and_quote_sizes_checked(self):
        d=AlpacaData(transport=lambda path:{'next_page_token':'next','bars':[]})
        with self.assertRaises(ValueError):d.candles('AAPL',NOW)
        d=AlpacaData(transport=lambda path:{'quote':dict(bp=100,ap=101,t=NOW.isoformat(),bs=0,**{'as':1})})
        self.assertFalse(d.quotes(['AAPL'])['AAPL']['tradeable'])
    def test_bad_ohlc_rejected(self):
        with self.assertRaises(ValueError):validate_bars([dict(timestamp=NOW,open=100,high=90,low=80,close=100,volume=1)])
    def test_history_failure_keeps_fresh_quote_stops_active(self):
        with tempfile.TemporaryDirectory() as folder:
            b=CryptoBook(folder+'/book.db',default_config('crypto'));b.process(quotes('BTC_USDT',60000),decision('BTC_USDT'),'open',NOW)
            class Feed:
                market='crypto';source='test'
                def market_open(self):return True
                def quotes(self,symbols):return quotes('BTC_USDT',57000,NOW+timedelta(seconds=1))
                def candles(self,*args):raise ValueError('No history')
            r=tick(Feed(),b,['BTC_USDT'],now=NOW+timedelta(seconds=1))
            self.assertEqual(r['fills'][0]['reason'],'stop');self.assertEqual(b.snapshot()['positions'],{})
    def test_closed_stock_session_no_new_entries(self):
        class Feed:
            market='stock';source='test'
            def market_open(self):return False
            def quotes(self,*args):raise AssertionError('Closed session must not fetch quotes')
        with tempfile.TemporaryDirectory() as folder:
            b=StockBook(folder+'/book.db',default_config('stock'));self.assertEqual(tick(Feed(),b,['AAPL'],now=NOW)['status'],'market_closed')
    def test_demo_both_markets_executes_and_duplicate_symbols_rejected(self):
        for market,book,symbol in [('stock',StockBook,'AAPL'),('crypto',CryptoBook,'BTC_USDT')]:
            with tempfile.TemporaryDirectory() as folder:
                b=book(folder+'/book.db',default_config(market));d=DemoData(market)
                self.assertEqual(tick(d,b,[symbol])['status'],'paper')
                with self.assertRaises(ValueError):tick(d,b,[symbol,symbol])

class SlowRequestClockTests(unittest.TestCase):
    def test_quote_collected_after_signal_clock_is_validated_at_execution(self):
        from unittest.mock import patch
        from brobs.fx_runner import tick as fx_tick
        later=NOW+timedelta(seconds=20)
        class Feed:
            source='slow fixture'
            def account_summary(self):return {'currency':'USD'}
            def candles(self,**kwargs):return [dict(timestamp=NOW-timedelta(hours=100-i),close=1.08+i*.0001) for i in range(100)]
            def quotes(self,pairs):return quotes('EUR_USD',1.1,later)
        with tempfile.TemporaryDirectory() as folder:
            b=FXBook(folder+'/book.db')
            with patch('brobs.fx_runner.datetime') as clock:
                clock.now.side_effect=[NOW,later]
                self.assertEqual(fx_tick(Feed(),b)['status'],'paper')
            self.assertEqual(b.snapshot()['last_tick'],later.isoformat())

class IndicatorAndArchiveTests(unittest.TestCase):
    def test_wilder_rsi_edges(self):
        self.assertEqual(rsi([1]*20,2),50);self.assertEqual(rsi(list(range(1,21)),2),100)
        self.assertEqual(rsi(list(range(20,0,-1)),2),0)
    def test_future_bar_cannot_change_past_signal(self):
        rows=[dict(close=100+i*.1,high=101+i*.1,low=99+i*.1) for i in range(120)]
        before=signal(rows[:110],'rsi2_reversion');rows[119]['close']=1000000
        self.assertEqual(before,signal(rows[:110],'rsi2_reversion'))
        self.assertEqual(signal([dict(close=math.nan)]*120)[0],'hold')
    def archive(self,stamp):
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:z.writestr('sample.csv',f'{stamp},100,101,99,100,1,0,0,0,0,0,0\n')
        return stream.getvalue()
    def test_binance_microsecond_and_millisecond_timestamps(self):
        micro=normalize_archive(self.archive(1788220800000000));milli=normalize_archive(self.archive(1788220800000))
        self.assertEqual(micro,milli);self.assertTrue(micro[0][0].startswith('2026-09-01'))
    def test_checksum_failure_does_not_publish_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            p=folder+'/data.csv'
            with self.assertRaisesRegex(ValueError,'checksum'):download('BTCUSDT',['2026-09'],p,lambda url:b'0'*64 if url.endswith('CHECKSUM') else self.archive(1788220800000000))
            self.assertFalse(os.path.exists(p))
if __name__=='__main__':unittest.main()
