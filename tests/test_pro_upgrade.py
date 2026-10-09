import math,tempfile,unittest
import json,subprocess,sys
from pathlib import Path
from dataclasses import asdict
from datetime import datetime,timedelta,timezone
from brobs.fx import FXBook,FXConfig
from brobs.fx_runner import tick
from brobs.protections import EntryProtection,performance
from brobs.pro_signals import FeatureCache,features,decision
from brobs.strategy_lab import select

NOW=datetime(2026,9,1,12,tzinfo=timezone.utc)
def quote(price,at=NOW):return {'EUR_USD':dict(bid=price,ask=price,timestamp=at.isoformat(),tradeable=True)}
def proposal(action,ident):return {'EUR_USD':dict(id=ident,action=action)}
def rows(n=260):return [dict(timestamp=NOW+timedelta(hours=i),open=100+i*.1,high=101+i*.1,low=99+i*.1,close=100+i*.1,volume=10) for i in range(n)]

class ReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup);self.path=self.folder.name+'/book.db';self.book=FXBook(self.path)
    def test_history_failure_still_checks_fresh_quote_stop(self):
        self.book.process(quote(1.1),proposal('buy','one'),'open',NOW)
        class Feed:
            def account_summary(self):return {'currency':'USD'}
            def candles(self,**kwargs):raise OSError('history unavailable')
            def quotes(self,pairs):return quote(1.08,NOW+timedelta(seconds=1))
        with self.assertRaises(OSError):tick(Feed(),self.book,now=NOW+timedelta(seconds=1))
        state=self.book.snapshot();self.assertEqual(state['positions'],{});self.assertEqual(state['trades'][-1]['reason'],'stop')
    def test_failed_history_and_stale_quote_never_fabricates_stop(self):
        self.book.process(quote(1.1),proposal('buy','one'),'open',NOW)
        class Feed:
            def account_summary(self):return {'currency':'USD'}
            def candles(self,**kwargs):raise ValueError('bad history')
            def quotes(self,pairs):return quote(1.08,NOW-timedelta(hours=1))
        with self.assertRaises(ValueError):tick(Feed(),self.book,now=NOW+timedelta(seconds=1))
        self.assertIn('EUR_USD',self.book.snapshot()['positions']);self.assertEqual(self.book.snapshot()['stats']['closed_trades'],0)
    def test_cooldown_persists_and_unblocks_after_window(self):
        self.book.set_entry_protection(EntryProtection(cooldown_seconds=60))
        self.book.process(quote(1.1),proposal('buy','one'),'open',NOW)
        at=NOW+timedelta(seconds=1);self.book.process(quote(1.101,at),proposal('close','two'),'close',at)
        restarted=FXBook(self.path);at+=timedelta(seconds=1)
        result=restarted.process(quote(1.1,at),proposal('buy','three'),'blocked',at)
        self.assertEqual(result['fills'],[]);self.assertEqual(result['entry_vetoes'][0]['reason'],'cooldown')
        at+=timedelta(seconds=61);self.assertEqual(len(restarted.process(quote(1.1,at),proposal('buy','four'),'reopen',at)['fills']),1)
        self.assertEqual(restarted.snapshot()['entry_protection']['cooldown_seconds'],60)
    def test_loss_streak_guard_does_not_block_exits(self):
        self.book.set_entry_protection(EntryProtection(loss_streak_limit=2,loss_window_seconds=300))
        for i in range(2):
            at=NOW+timedelta(seconds=i*2);self.book.process(quote(1.1,at),proposal('buy',str(i)),'open'+str(i),at)
            at+=timedelta(seconds=1);self.book.process(quote(1.08,at),{},'stop'+str(i),at)
        at=NOW+timedelta(seconds=4);result=self.book.process(quote(1.1,at),proposal('buy','three'),'blocked',at)
        self.assertEqual(result['entry_vetoes'][0]['reason'],'loss_streak');self.assertEqual(self.book.snapshot()['stats']['losses'],2)
        at+=timedelta(seconds=301);self.assertEqual(len(self.book.process(quote(1.1,at),proposal('buy','four'),'unlocked',at)['fills']),1)
    def test_protection_validation(self):
        for args in [dict(cooldown_seconds=-1),dict(loss_streak_limit=21),dict(loss_streak_limit=True),dict(loss_window_seconds=0)]:
            with self.assertRaises(ValueError):EntryProtection(**args)
    def test_curve_and_expectancy_survive_restart(self):
        self.book.process(quote(1.1),proposal('buy','one'),'open',NOW)
        at=NOW+timedelta(seconds=1);self.book.process(quote(1.102,at),proposal('close','two'),'close',at)
        s=FXBook(self.path).snapshot();self.assertEqual(len(s['equity_history']),2)
        self.assertAlmostEqual(s['performance_detail']['expectancy_per_closed_trade'],s['stats']['net_pnl'],places=4)
    def test_pause_command_works_with_nondefault_risk_config(self):
        path=self.folder.name+'/custom.db';book=FXBook(path,FXConfig(stop_fraction=.004,risk_fraction=.01))
        subprocess.run([sys.executable,'-m','brobs.fx_runner','--db',path,'--pause'],check=True,capture_output=True)
        self.assertTrue(book.snapshot()['paused'])
        subprocess.run([sys.executable,'-m','brobs.fx_runner','--db',path,'--resume'],check=True,capture_output=True)
        self.assertFalse(book.snapshot()['paused'])
    def test_evidence_veto_blocks_entry_and_keeps_crypto_stops_active(self):
        from unittest.mock import patch
        from brobs.market_book import CryptoBook,default_config
        from brobs.market_runner import tick as market_tick
        book=CryptoBook(self.folder.name+'/crypto.db',default_config('crypto'));path=Path(self.folder.name)/'evidence.json';path.write_text('{}')
        history=rows(260)
        for i,r in enumerate(history):r['timestamp']=NOW-timedelta(hours=260-i)
        class Feed:
            market='crypto';source='fixture';at=NOW;price=100
            def market_open(self):return True
            def candles(self,*args):return history
            def quotes(self,*args):return {'BTC_USDT':dict(bid=self.price,ask=self.price,timestamp=self.at.isoformat(),tradeable=True)}
        feed=Feed()
        with patch('brobs.market_runner.signal',return_value=('buy',[])):
            result=market_tick(feed,book,['BTC_USDT'],now=NOW,evidence_report=path)
        self.assertEqual(result['fills'],[]);self.assertEqual(result['signals']['BTC_USDT']['votes'][-1]['action'],'veto')
        feed.at+=timedelta(seconds=1);book.process(feed.quotes(),{'BTC_USDT':dict(id='manual-fixture',action='buy')},'fixture-open',feed.at)
        feed.at+=timedelta(seconds=1);feed.price=95
        with patch('brobs.market_runner.signal',return_value=('hold',[])):
            result=market_tick(feed,book,['BTC_USDT'],now=feed.at,evidence_report=path)
        self.assertEqual(result['fills'][0]['reason'],'stop');self.assertEqual(book.snapshot()['positions'],{})

class ResearchTests(unittest.TestCase):
    def test_feature_cache_prefix_is_unchanged_by_future_bars(self):
        data=rows();prefix=FeatureCache(data[:220]);full=FeatureCache(data)
        self.assertEqual(prefix.values[data[219]['timestamp']],full.values[data[219]['timestamp']])
        data[-1]['close']=9999
        self.assertEqual(full.values[data[219]['timestamp']],FeatureCache(data).values[data[219]['timestamp']])
    def test_range_entry_cost_hurdle_and_exit(self):
        f=dict(last=90,previous=92,center=100,scale=4,previous_center=100,previous_scale=4,rsi=20,ema50=100,ema200=100,histogram=0,previous_histogram=0,efficiency=.2)
        self.assertEqual(decision(f,'range_reversion')[0],'buy')
        self.assertEqual(decision(f,'range_reversion',roundtrip_cost=.09)[0],'hold')
        f['last']=101;self.assertEqual(decision(f,'range_reversion',side=1)[0],'close')
    def test_macd_requires_real_cross_and_respects_long_only(self):
        f=dict(last=110,previous=109,center=110,scale=1,previous_center=109,previous_scale=1,rsi=55,ema50=108,ema200=100,histogram=1,previous_histogram=-1,efficiency=.8)
        self.assertEqual(decision(f,'macd_swing')[0],'buy')
        f['previous_histogram']=1;self.assertEqual(decision(f,'macd_swing')[0],'hold')
        f.update(last=90,rsi=40,histogram=-1,previous_histogram=1)
        self.assertEqual(decision(f,'macd_swing')[0],'hold');self.assertEqual(decision(f,'macd_swing',allow_short=True)[0],'sell')
    def test_selector_requires_both_profitable_folds_and_stress(self):
        valid=dict(closed_trades=20,net_pnl=10,profit_factor=1.2,return_pct=.1)
        a=dict(parameters={'name':'a'},validation_folds=[valid,valid],cost_stress={'net_pnl':1})
        b=dict(parameters={'name':'b'},validation_folds=[{**valid,'net_pnl':-1},valid],cost_stress={'net_pnl':100})
        self.assertEqual(select([a,b]),a);self.assertIsNone(select([b]))
        self.assertIsNone(select([{**a,'cost_stress':{'net_pnl':-1}}]))
    def test_performance_does_not_confuse_win_rate_with_expectancy(self):
        p=performance([{'pnl':1},{'pnl':1},{'pnl':1},{'pnl':-10}])
        self.assertEqual(p['expectancy_per_closed_trade'],-1.75);self.assertEqual(p['payoff_ratio'],.1)
    def test_evidence_gate_checks_samples_costs_and_finite_metrics(self):
        from brobs.evidence import gate
        proposal=dict(id='one',action='buy',votes=[]);cfg=FXConfig()
        report=dict(market='forex',symbol='EUR_USD',historical_acceptance=True,selected_parameters=dict(family='trend',threshold=10,stop_fraction=.005,reward_risk=2),
            selected_later=dict(closed_trades=100,net_pnl=10,profit_factor=1.3),selected_later_stress=dict(net_pnl=1),selected_later_folds=[dict(net_pnl=1)]*3)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'report.json';path.write_text(json.dumps(report))
            self.assertEqual(gate(proposal,path,'forex','EUR_USD','trend',None,cfg)['action'],'buy')
            self.assertEqual(gate(proposal,path,'forex','GBP_USD','trend',None,cfg)['action'],'hold')
            for value in (0,-1,math.nan,True):
                report['selected_later_stress']['net_pnl']=value;path.write_text(json.dumps(report))
                self.assertEqual(gate(proposal,path,'forex','EUR_USD','trend',None,cfg)['action'],'hold')
            path.write_text('{}');self.assertEqual(gate(proposal,path,'forex','EUR_USD','trend',None,cfg)['action'],'hold')
    def test_canonical_merge_rejects_duplicate_and_mixed_inputs(self):
        from brobs.history_merge import merge
        import csv
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/'one.csv'
            with source.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['timestamp','open','high','low','close','volume']);w.writeheader()
                for r in rows(40):w.writerow({**r,'timestamp':r['timestamp'].isoformat()})
            source.with_suffix('.provenance.json').write_text(json.dumps(dict(symbol='BTCUSDT',quote_currency='USDT',sources=[])))
            out=Path(folder)/'out.csv';r=merge([source],out)
            self.assertEqual(r['rows'],40);self.assertEqual(len(r['normalized_csv_sha256']),64)
            with self.assertRaises(ValueError):merge([source,source],out)
