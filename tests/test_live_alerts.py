import tempfile,threading,unittest
from datetime import datetime,timezone
from brobs.live_alerts import LiveAlertService
from brobs.live_orders import LiveOrders
from test_live_orders import FakeBroker,NOW,ACCT  # tests dir is on sys.path under discover

SECRET='s'*32
class PricingBroker(FakeBroker):
    def __call__(self,method,path,payload=None):
        if method=='GET' and '/pricing' in path:
            return dict(prices=[dict(instrument='EUR_USD',time=NOW.isoformat(),status='tradeable',bids=[dict(price='1.1000')],asks=[dict(price='1.1001')])])
        return super().__call__(method,path,payload)

class LiveAlertTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.db=self.folder.name+'/live.db';self.broker=PricingBroker()
    def service(self,broker=None):
        gateway=LiveOrders(self.db,'practice','tok-123456',ACCT,None,None,broker or self.broker,{})
        return LiveAlertService(SECRET,gateway,self.db,10000,clock=lambda:NOW)
    def alert(self,event='e1',action='buy',**extra):
        return dict(secret=SECRET,event_id=event,symbol='EUR_USD',market='forex',action=action,**extra)

    def test_rejects_weak_secret_and_bad_secret_without_touching_broker(self):
        with self.assertRaises(ValueError):LiveAlertService('short',self.service().gateway,self.db,10000)
        s=self.service();bad=self.alert();bad['secret']='x'*32
        with self.assertRaises(PermissionError):s.handle(bad)
        self.assertEqual(self.broker.calls,[])
    def test_buy_places_one_order_via_broker_quotes(self):
        r=self.service().handle(self.alert(price=1.10005))
        self.assertEqual((r['status'],r['environment']),('filled','practice'));self.assertEqual(self.broker.posts(),1)
    def test_duplicate_is_ignored_even_after_restart(self):
        self.service().handle(self.alert())
        self.assertEqual(self.service().handle(self.alert())['status'],'duplicate')   # new service, same journal
        self.assertEqual(self.broker.posts(),1)
    def test_simultaneous_identical_deliveries_place_exactly_one_order(self):
        s=self.service();results=[];errors=[]
        def hit():
            try:results.append(s.handle(self.alert('race'))['status'])
            except Exception as e:errors.append(e)
        threads=[threading.Thread(target=hit) for _ in range(12)]
        [t.start() for t in threads];[t.join() for t in threads]
        self.assertEqual(self.broker.posts(),1);self.assertEqual(results.count('duplicate'),11);self.assertEqual(errors,[])
    def test_alert_price_far_from_broker_quote_is_rejected_and_consumed(self):
        s=self.service()
        with self.assertRaises(ValueError):s.handle(self.alert('stale',price=1.2000))
        self.assertEqual(self.broker.posts(),0)
        self.assertEqual(s.handle(self.alert('stale',price=1.1000))['status'],'duplicate')   # failed events are not replayed
    def test_unsupported_market_symbol_or_action_rejected_before_claim(self):
        s=self.service()
        for bad in (dict(market='crypto'),dict(symbol='BTC_USDT'),dict(action='short')):
            with self.assertRaises(ValueError):s.handle({**self.alert('x'),**bad})
        self.assertEqual(s.handle(self.alert('x'))['status'],'filled')   # 'x' was never consumed by the rejects
    def test_broker_failure_propagates_and_consumes_event(self):
        from brobs.live_orders import LiveOrders
        s=self.service(PricingBroker(post_error=TimeoutError('?')))
        with self.assertRaises(TimeoutError):s.handle(self.alert('t'))
        self.assertEqual(s.handle(self.alert('t'))['status'],'duplicate')
    def test_close_flattens_only_that_pair(self):
        r=self.service().handle(self.alert('c',action='close'))
        self.assertEqual((r['status'],r['closed']),('flattened',['7']))

if __name__=='__main__':unittest.main()
