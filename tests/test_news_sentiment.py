"""No-cost news provenance and conservative paper-entry gate regression tests."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from brobs.news_sentiment import (
    GDELT_URL, evaluate_articles, get_news_review, guard_entry,
)
from brobs.market_book import CryptoBook, default_config
from brobs.market_runner import tick

NOW = datetime(2026, 10, 10, 12, tzinfo=timezone.utc)
def article(domain, title, age=1, urlhost=None, language='English'):
    stamp=(NOW-timedelta(hours=age)).strftime('%Y%m%dT%H%M%SZ')
    host=urlhost or ('www.' + domain)
    return {'domain':domain,'url':'https://'+host+'/'+str(abs(hash(title)))+'/'+title.split()[0],
            'title':title,'seendate':stamp,'language':language}
def fake(articles):
    def fetch(url):
        assert url.startswith(GDELT_URL+'?'),url
        return json.dumps({'articles':articles}).encode('utf8')
    return fetch

POSITIVE=[
    article('reuters.com','Bitcoin rallies following new institutional interest'),
    article('cnbc.com','Bitcoin recovery supported by strong demand'),
]
NEGATIVE=[
    article('reuters.com','Bitcoin exchange hacked amid security breach'),
    article('cnbc.com','Bitcoin fraud investigation expands'),
]
class NewsSafetyTests(unittest.TestCase):
    def test_recent_diverse_provenance_reports_headline_tone_not_win_probability(self):
        review=get_news_review('BTC_USDT',NOW,fetch=fake(POSITIVE))
        self.assertEqual(review['status'],'verified_metadata')
        self.assertEqual(review['sentiment'],'positive')
        self.assertEqual(len(review['articles']),2)
        self.assertIn('truth NOT verified',review['reason'])
        result=guard_entry({'action':'buy','votes':[{'agent':'trend','action':'buy'}]},'BTC_USDT',NOW,fetch=fake(POSITIVE))
        self.assertEqual(result['action'],'buy')
        self.assertEqual(result['votes'][-1]['action'],'clear')
        self.assertEqual(len(result['votes'][-1]['sources']),2)
    def test_two_independent_negative_publishers_block_new_entry(self):
        result=guard_entry({'action':'buy','votes':[]},'BTC_USDT',NOW,fetch=fake(NEGATIVE))
        self.assertEqual(result['action'],'hold')
        self.assertEqual(result['votes'][-1]['sentiment'],'negative')
    def test_stale_missing_and_unrelated_sources_cannot_unlock(self):
        bad=[
            article('reuters.com','Bitcoin rallied last month',age=48),
            article('unknown.scam','Bitcoin rallies in fake headlines',urlhost='unknown.scam'),
            article('cnbc.com','ETH hits new highs'),
            article('reuters.com','Bitcoin rallies today',language='French'),
        ]
        review=evaluate_articles('BTC_USDT',bad,NOW)
        self.assertEqual(review['status'],'insufficient')
        self.assertEqual(guard_entry({'action':'buy','votes':[]},'BTC_USDT',NOW,fetch=fake(bad))['action'],'hold')
    def test_one_publisher_cannot_fake_diversity_with_multiple_urls(self):
        dup=[article('reuters.com','Bitcoin surges again'),
             article('reuters.com','Bitcoin rally accelerates')]
        self.assertEqual(get_news_review('BTC_USDT',NOW,fetch=fake(dup))['status'],'insufficient')
    def test_unavailable_provider_and_unsupported_assets_fail_closed(self):
        def error(url):
            raise TimeoutError('no response')
        result=guard_entry({'action':'buy','votes':[]},'BTC_USDT',NOW,fetch=error)
        self.assertEqual(result['action'],'hold')
        self.assertEqual(result['votes'][-1]['action'],'veto')
        self.assertEqual(get_news_review('NVDA',NOW,fetch=fake(POSITIVE))['status'],'unsupported')
    def test_malicious_publisher_host_and_future_article_rejected(self):
        attack=[
            article('reuters.com','Bitcoin rallies',urlhost='reuters.com.attacker.com'),
            article('cnbc.com','Bitcoin upgrade announced',age=-1),
        ]
        self.assertEqual(evaluate_articles('BTC_USDT',attack,NOW)['status'],'insufficient')
    def test_news_gate_does_not_override_closed_position_exits(self):
        with tempfile.TemporaryDirectory() as folder:
            book=CryptoBook(folder+'/paper.db',default_config('crypto'))
            history=[]
            for i in range(100):
                at=NOW-timedelta(hours=101-i)
                history.append({'timestamp':at,'open':60000+i,'high':60100+i,'low':59900+i,
                                'close':60000+i,'volume':10})
            class Feed:
                market='crypto'
                source='fixture'
                price=60000
                def market_open(self): return True
                def candles(self,symbol,now): return history
                def quotes(self,symbols):
                    return {'BTC_USDT':{'bid':self.price,'ask':self.price,'timestamp':NOW.isoformat(),'tradeable':True}}
            feed=Feed()
            with patch('brobs.market_runner.signal',return_value=('buy',[])):
                result=tick(feed,book,['BTC_USDT'],now=NOW,news_guard=True,news_fetch=fake(NEGATIVE))
                self.assertEqual(result['fills'],[])
                result=tick(feed,book,['BTC_USDT'],now=NOW+timedelta(seconds=2),news_guard=True,news_fetch=fake(POSITIVE))
                # Different quote IDs are required for a fresh tick; the stock/crypto
                # broker may apply its own constraints before entry.
                self.assertEqual(result['status'] in ('paper','duplicate_tick'),True)
            # Simulate an existing position independently of news.
            self.assertEqual(get_news_review('BTC_USDT',NOW,fetch=fake(NEGATIVE))['sentiment'],'negative')
            # Directly exercise the signal-independent protective stop path.
            book.process({'BTC_USDT':{'bid':60000,'ask':60000,'timestamp':NOW.isoformat(),'tradeable':True}},
                         {'BTC_USDT':{'id':'opening','action':'buy'}},'manual-open',NOW)
            self.assertTrue(book.snapshot()['positions'])
            feed.price=56000
            feed.quotes=lambda symbols:{'BTC_USDT':{'bid':56000,'ask':56000,
                'timestamp':(NOW+timedelta(seconds=4)).isoformat(),'tradeable':True}}
            with patch('brobs.market_runner.signal',return_value=('hold',[])):
                tick(feed,book,['BTC_USDT'],now=NOW+timedelta(seconds=4),news_guard=True,news_fetch=fake(NEGATIVE))
            self.assertEqual(book.snapshot()['positions'],{})

if __name__=='__main__':unittest.main()
