import tempfile,unittest,sqlite3
from datetime import datetime,timedelta,timezone
from brobs.practice_orders import entry_plan,PracticeOrders

NOW=datetime(2026,10,9,10,tzinfo=timezone.utc)
def quotes(at=NOW):return {'EUR_USD':dict(bid=1.1,ask=1.1001,timestamp=at.isoformat(),tradeable=True)}
def account():return dict(account=dict(currency='USD',NAV='10000',openTradeCount=0,pendingOrderCount=0))

class PracticeGatewayTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.path=self.folder.name+'/orders.db';self.calls=[]
        self.plan=entry_plan('EUR_USD','buy','H1:bar',quotes(),10,NOW)
    def gateway(self,response=None):
        def transport(method,path,payload=None):
            self.calls.append((method,path,payload))
            if method=='GET':
                if path.endswith('/summary'):return account()
                return dict(trade=dict(state='OPEN',stopLossOrder=dict(state='PENDING'),takeProfitOrder=dict(state='PENDING')))
            return response or dict(orderFillTransaction=dict(id='42',tradeOpened=dict(tradeID='42')))
        return PracticeOrders(self.path,'fake-token','101-123-456',transport)
    def test_brackets_and_no_leverage_notional_cap(self):
        o=self.plan['order'];self.assertEqual(o['units'],'1')
        self.assertLess(float(o['stopLossOnFill']['price']),float(o['priceBound']))
        self.assertGreater(float(o['takeProfitOnFill']['price']),float(o['priceBound']))
        self.assertEqual(o['timeInForce'],'FOK');self.assertEqual(o['positionFill'],'OPEN_ONLY')
        self.assertLessEqual(int(o['units'])*float(o['priceBound']),2)
    def test_short_bracket_direction_and_stable_identifier(self):
        p=entry_plan('EUR_USD','sell','H1:bar',quotes(),10,NOW)
        self.assertEqual(p['order']['clientExtensions']['id'],self.plan['order']['clientExtensions']['id'])
        self.assertLess(int(p['order']['units']),0)
        self.assertGreater(float(p['order']['stopLossOnFill']['price']),float(p['order']['priceBound']))
    def test_fill_and_restart_never_resubmit_same_signal(self):
        g=self.gateway();self.assertEqual(g.submit(self.plan,quotes(),NOW)['status'],'filled')
        with self.assertRaises(ValueError):self.gateway().submit(self.plan,quotes(),NOW)
        self.assertEqual(sum(m=='POST' for m,_,_ in self.calls),1)
    def test_timeout_halts_all_new_attempts_even_after_restart(self):
        def transport(method,path,payload=None):
            if method=='GET':return account()
            raise TimeoutError('Unknown outcome')
        g=PracticeOrders(self.path,'fake-token','101-123-456',transport)
        with self.assertRaises(TimeoutError):g.submit(self.plan,quotes(),NOW)
        other=entry_plan('EUR_USD','buy','next-bar',quotes(),10,NOW)
        with self.assertRaises(ValueError):self.gateway().submit(other,quotes(),NOW)
        self.assertEqual(self.calls,[])
    def test_tampered_size_or_missing_stop_never_posts(self):
        import copy
        for mutate in ('units','stop'):
            p=copy.deepcopy(self.plan)
            if mutate=='units':p['order']['units']='100000'
            else:del p['order']['stopLossOnFill']
            with self.assertRaises(ValueError):self.gateway().submit(p,quotes(),NOW)
        self.assertTrue(all(m=='GET' for m,_,_ in self.calls))
    def test_stale_plan_and_live_environment_rejected_before_network(self):
        for p,now in [(self.plan,NOW+timedelta(seconds=31)),({**self.plan,'environment':'live'},NOW)]:
            with self.assertRaises(ValueError):self.gateway().submit(p,quotes(now),now)
        self.assertEqual(self.calls,[])
    def test_existing_broker_position_blocks_entry(self):
        def transport(method,path,payload=None):
            self.assertEqual(method,'GET');r=account();r['account']['openTradeCount']=1;return r
        g=PracticeOrders(self.path,'fake-token','101-123-456',transport)
        with self.assertRaises(ValueError):g.submit(self.plan,quotes(),NOW)
    def test_journal_cannot_be_reused_for_another_account(self):
        self.gateway()
        with self.assertRaises(ValueError):PracticeOrders(self.path,'fake-token','101-999-456',lambda *a:None)
    def test_cancelled_order_is_not_reported_as_fill(self):
        g=self.gateway(dict(orderCancelTransaction=dict(reason='FOK')))
        self.assertEqual(g.submit(self.plan,quotes(),NOW)['status'],'cancelled')
    def test_missing_trade_reference_blocks_new_entries(self):
        g=self.gateway(dict(orderFillTransaction=dict(id='42')))
        self.assertEqual(g.submit(self.plan,quotes(),NOW)['status'],'filled_unverified_protection')
        with self.assertRaises(ValueError):g.submit(entry_plan('EUR_USD','buy','other',quotes(),10,NOW),quotes(),NOW)
    def test_missing_broker_bracket_is_not_confirmed_as_protected_fill(self):
        def transport(method,path,payload=None):
            if method=='POST':return dict(orderFillTransaction=dict(tradeOpened=dict(tradeID='42')))
            if path.endswith('/summary'):return account()
            return dict(trade=dict(state='OPEN',stopLossOrder=dict(state='PENDING')))
        g=PracticeOrders(self.path,'fake-token','101-123-456',transport)
        self.assertEqual(g.submit(self.plan,quotes(),NOW)['status'],'filled_unverified_protection')
    def test_invalid_quote_never_creates_a_plan(self):
        for q in (quotes(NOW-timedelta(hours=1)),{'EUR_USD':dict(bid=1.1,ask=1.2,timestamp=NOW.isoformat(),tradeable=True)}):
            with self.assertRaises(ValueError):entry_plan('EUR_USD','buy','bar',q,10,NOW)
