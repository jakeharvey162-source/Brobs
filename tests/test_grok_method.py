import copy,json,tempfile,unittest
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
from brobs.grok_method import complete_four_hour_closes,consensus
from brobs.market_runner import tick
from brobs.market_book import CryptoBook,default_config
from brobs.grok_review import request_for,gate,write_json,review_with_xai

NOW=datetime(2026,9,1,12,tzinfo=timezone.utc)
def bars():
    return [dict(timestamp=NOW-timedelta(hours=120-i),open=100+i*.1,high=100.2+i*.1,low=99.8+i*.1,close=100+i*.1,volume=10) for i in range(120)]

class GrokTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.book=CryptoBook(self.folder.name+'/book.db',default_config('crypto'))
        self.path=self.folder.name+'/review.json'
        self.proposal=dict(id='bar1',action='buy',votes=[])
        self.request=request_for(self.book,'BTC_USDT',bars(),self.proposal,NOW)
    def review(self,**updates):
        value=dict(request_id=self.request['request_id'],created_at=NOW.isoformat(),decision='approve',reason='Fixture, not real model evidence',model='grok-fixture')
        value.update(updates);write_json(self.path,value)
    def test_partial_four_hour_bucket_excluded(self):
        rows=bars();self.assertEqual(len(complete_four_hour_closes(rows)),30)
        self.assertEqual(len(complete_four_hour_closes(rows[:-1])),29)
        self.assertEqual(len(complete_four_hour_closes(rows[1:])),29)
    def test_gaps_abstain_and_flat_history_no_entry(self):
        rows=bars();rows.pop(-2)
        self.assertEqual(consensus(rows)[0],'hold')
        self.assertEqual(consensus(rows)[1][0]['action'],'veto')
        self.assertEqual(consensus(bars())[0],'hold')
    def test_invalid_ohlc_rejected(self):
        rows=bars();rows[-1]['high']=1
        with self.assertRaises(ValueError):consensus(rows)
    def test_approve_preserves_action_and_size_contract(self):
        self.review();result=gate(self.proposal,self.request,self.path,NOW)
        self.assertEqual(result['action'],'buy');self.assertEqual(result['id'],'bar1')
        self.review(size=100000)
        self.assertEqual(gate(self.proposal,self.request,self.path,NOW)['action'],'hold')
    def test_missing_mismatched_expired_future_malformed_veto(self):
        self.assertEqual(gate(self.proposal,self.request,self.path,NOW)['action'],'hold')
        for updates in [dict(request_id='wrong'),dict(created_at=(NOW-timedelta(seconds=901)).isoformat()),dict(created_at=(NOW+timedelta(seconds=1)).isoformat()),dict(decision='buy'),dict(reason=1)]:
            self.review(**updates);self.assertEqual(gate(self.proposal,self.request,self.path,NOW)['action'],'hold')
    def test_xai_transport_fixture_schema_no_tools_or_orders(self):
        seen=[]
        def send(payload,key):
            seen.append(payload);return dict(choices=[dict(message=dict(content=json.dumps(dict(decision='approve',reason='Fixture'))))])
        result=review_with_xai(self.request,'grok-fixture','dummy',NOW,send)
        self.assertEqual(result['request_id'],self.request['request_id']);self.assertEqual(result['decision'],'approve')
        self.assertEqual(seen[0]['response_format']['type'],'json_schema');self.assertNotIn('tools',seen[0])
    def test_changed_evidence_or_expired_request_never_calls_api(self):
        req=copy.deepcopy(self.request);req['evidence']['symbol']='ETH_USDT'
        def send(*args):raise AssertionError('Must not call transport')
        with self.assertRaises(ValueError):review_with_xai(req,'grok-fixture','dummy',NOW,send)
        with self.assertRaises(ValueError):review_with_xai(self.request,'grok-fixture','dummy',NOW+timedelta(minutes=16),send)
    def test_pending_then_approved_same_bar_enters_once(self):
        class Feed:
            market='crypto';source='fixture'
            def market_open(self):return True
            def candles(self,*args):return bars()
            def quotes(self,*args):return {'BTC_USDT':dict(bid=112,ask=112,timestamp=self.at.isoformat(),tradeable=True)}
        feed=Feed();feed.at=NOW;request_path=self.folder.name+'/request.json'
        with patch('brobs.market_runner.signal',return_value=('buy',[])):
            result=tick(feed,self.book,['BTC_USDT'],now=NOW,grok_review=self.path,grok_request=request_path)
            self.assertEqual(result['fills'],[])
            with open(request_path) as f:req=json.load(f)
            self.review(request_id=req['request_id'])
            feed.at=NOW+timedelta(seconds=1)
            result=tick(feed,self.book,['BTC_USDT'],now=feed.at,grok_review=self.path,grok_request=request_path)
            self.assertEqual(len(result['fills']),1)
            feed.at+=timedelta(seconds=1)
            self.assertEqual(tick(feed,self.book,['BTC_USDT'],now=feed.at,grok_review=self.path)['fills'],[])
    def test_stop_and_strategy_close_bypass_missing_review(self):
        self.book.process({'BTC_USDT':dict(bid=100,ask=100,timestamp=NOW.isoformat(),tradeable=True)}, {'BTC_USDT':self.proposal},'open',NOW)
        class Feed:
            market='crypto';source='fixture'
            def market_open(self):return True
            def candles(self,*args):return bars()
            def quotes(self,*args):return {'BTC_USDT':dict(bid=90,ask=90,timestamp=(NOW+timedelta(seconds=1)).isoformat(),tradeable=True)}
        with patch('brobs.market_runner.signal',return_value=('hold',[])):
            result=tick(Feed(),self.book,['BTC_USDT'],now=NOW+timedelta(seconds=1),grok_review=self.path)
        self.assertEqual(result['fills'][0]['reason'],'stop')
    def test_request_export_alone_does_not_authorize_entry(self):
        class Feed:
            market='crypto';source='fixture'
            def market_open(self):return True
            def candles(self,*args):return bars()
            def quotes(self,*args):return {'BTC_USDT':dict(bid=112,ask=112,timestamp=NOW.isoformat(),tradeable=True)}
        path=self.folder.name+'/request.json'
        with patch('brobs.market_runner.signal',return_value=('buy',[])):
            result=tick(Feed(),self.book,['BTC_USDT'],now=NOW,grok_request=path)
        self.assertEqual(result['fills'],[])
        with open(path) as f:self.assertEqual(json.load(f)['evidence']['symbol'],'BTC_USDT')
    def test_strategy_close_is_not_blocked_by_review(self):
        self.book.process({'BTC_USDT':dict(bid=100,ask=100,timestamp=NOW.isoformat(),tradeable=True)}, {'BTC_USDT':self.proposal},'open',NOW)
        class Feed:
            market='crypto';source='fixture'
            def market_open(self):return True
            def candles(self,*args):return bars()
            def quotes(self,*args):return {'BTC_USDT':dict(bid=100,ask=100,timestamp=(NOW+timedelta(seconds=1)).isoformat(),tradeable=True)}
        with patch('brobs.market_runner.signal',return_value=('close',[])):
            result=tick(Feed(),self.book,['BTC_USDT'],now=NOW+timedelta(seconds=1),grok_review=self.path)
        self.assertEqual(len(result['fills']),1);self.assertEqual(self.book.snapshot()['positions'],{})
