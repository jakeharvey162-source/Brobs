import os,tempfile,unittest
from datetime import datetime,timedelta,timezone
from brobs.live_orders import LiveOrders,LiveLimits,ARM_PHRASE

NOW=datetime(2026,10,9,10,tzinfo=timezone.utc)
ACCT='101-123-456'
def quotes(at=NOW):return {'EUR_USD':dict(bid=1.1,ask=1.1001,timestamp=at.isoformat(),tradeable=True)}
LIVE_ENV={'BROBS_LIVE_ARM':ARM_PHRASE}

class FakeBroker:
    def __init__(self,nav='10000',open_trades=0,post_error=None,order_lookup=None):
        self.nav=nav;self.open=open_trades;self.post_error=post_error;self.order_lookup=order_lookup;self.calls=[]
        self.trades=[dict(id='7',instrument='EUR_USD'),dict(id='8',instrument='GBP_USD')]
    def __call__(self,method,path,payload=None):
        self.calls.append((method,path,payload))
        if method=='GET' and path.endswith('/summary'):
            return dict(account=dict(currency='USD',NAV=self.nav,openTradeCount=self.open,pendingOrderCount=0))
        if method=='GET' and '/orders/@' in path:return self.order_lookup(path) if self.order_lookup else {'_status':404}
        if method=='GET' and '/trades/' in path:
            return dict(trade=dict(state='OPEN',stopLossOrder=dict(state='PENDING'),takeProfitOrder=dict(state='PENDING')))
        if method=='GET' and path.endswith('/openTrades'):return dict(trades=self.trades)
        if method=='GET' and path.endswith('/pendingOrders'):return dict(orders=[dict(id='9')])
        if method=='PUT':return {}
        if method=='POST':
            if self.post_error:raise self.post_error
            return dict(orderFillTransaction=dict(id='42',tradeOpened=dict(tradeID='42')))
        raise AssertionError((method,path))
    def posts(self):return sum(m=='POST' for m,_,_ in self.calls)

class LiveGatewayTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory();self.addCleanup(self.folder.cleanup)
        self.db=self.folder.name+'/live.db';self.stop=self.folder.name+'/STOP'
    def live(self,broker=None,limits=None,env=None,**kw):
        broker=broker or FakeBroker()
        g=LiveOrders(self.db,'live','tok-123456',ACCT,limits,self.stop,broker,env if env is not None else LIVE_ENV,**kw)
        return g,broker
    def plan(self,g,signal='bar-1'):return g.plan('EUR_USD','buy',signal,quotes(),10000,NOW)

    def test_live_is_disarmed_by_default_and_phrase_must_match_exactly(self):
        for env in ({},{'BROBS_LIVE_ARM':'yes'},{'BROBS_LIVE_ARM':ARM_PHRASE.lower()}):
            with self.assertRaises(PermissionError):LiveOrders(self.db,'live','tok-123456',ACCT,None,self.stop,FakeBroker(),env)
    def test_live_requires_an_operator_stop_file_path(self):
        with self.assertRaises(ValueError):LiveOrders(self.db,'live','tok-123456',ACCT,None,None,FakeBroker(),LIVE_ENV)
    def test_practice_needs_no_arming(self):
        g=LiveOrders(self.db,'practice','tok-123456',ACCT,None,None,FakeBroker(),{})
        self.assertEqual(g.plan('EUR_USD','buy','x',quotes(),10000,NOW)['order']['clientExtensions']['tag'],'BROBS_PRACTICE')
    def test_live_uses_live_host_and_label(self):
        g,_=self.live()
        self.assertEqual(g.base,'https://api-fxtrade.oanda.com')
        p=self.plan(g);self.assertEqual(p['environment'],'live');self.assertEqual(p['order']['clientExtensions']['tag'],'BROBS_LIVE')
    def test_fill_sends_one_bracketed_order_and_never_resends(self):
        g,b=self.live();p=self.plan(g)
        self.assertEqual(g.submit(p,quotes(),NOW)['status'],'filled')
        o=[c[2] for c in b.calls if c[0]=='POST'][0]['order']
        self.assertEqual((o['timeInForce'],o['positionFill']),('FOK','OPEN_ONLY'));self.assertIn('stopLossOnFill',o)
        g2,b2=self.live()
        with self.assertRaises(ValueError):g2.submit(p,quotes(),NOW)
        self.assertEqual(b2.posts(),0)
    def test_stop_file_blocks_new_entries(self):
        g,b=self.live();p=self.plan(g);open(self.stop,'w').close()
        with self.assertRaises(PermissionError):g.submit(p,quotes(),NOW)
        self.assertEqual(b.posts(),0)
    def test_max_units_ceiling_clamps_the_order(self):
        g,b=self.live(limits=LiveLimits(max_units=10));p=self.plan(g)
        self.assertEqual(p['order']['units'],'10');g.submit(p,quotes(),NOW)
        self.assertEqual([c[2] for c in b.calls if c[0]=='POST'][0]['order']['units'],'10')
    def test_orders_per_day_limit(self):
        g,b=self.live(limits=LiveLimits(max_orders_per_day=1));g.submit(self.plan(g,'a'),quotes(),NOW)
        with self.assertRaises(PermissionError):g.submit(self.plan(g,'b'),quotes(),NOW)
        self.assertEqual(b.posts(),1)
    def test_daily_loss_limit_halts_entries_after_nav_drop(self):
        g,b=self.live();g.submit(self.plan(g,'a'),quotes(),NOW)
        b.nav='9700'  # -3% vs the 10,000 start-of-day NAV, limit is 2%
        with self.assertRaises(PermissionError):g.submit(self.plan(g,'b'),quotes(),NOW)
        self.assertEqual(b.posts(),1)
    def test_open_trade_blocks_second_entry(self):
        g,b=self.live(FakeBroker(open_trades=1))
        with self.assertRaises(ValueError):g.submit(self.plan(g),quotes(),NOW)
    def test_hard_ceilings_cannot_be_exceeded_by_configuration(self):
        for bad in (dict(max_units=10**6),dict(max_orders_per_day=99),dict(max_daily_loss_fraction=.5),dict(max_units=True)):
            with self.assertRaises(ValueError):LiveLimits(**bad)
    def test_journal_is_bound_to_one_account_and_environment(self):
        self.live()
        with self.assertRaises(ValueError):LiveOrders(self.db,'live','tok-123456','999-888-777',None,self.stop,FakeBroker(),LIVE_ENV)

    def test_timeout_blocks_everything_then_reconcile_recovers_from_broker_truth(self):
        found={'order':dict(state='FILLED',tradeOpenedID='42')}
        g,b=self.live(FakeBroker(post_error=TimeoutError('?'),order_lookup=lambda path:found))
        with self.assertRaises(TimeoutError):g.submit(self.plan(g,'a'),quotes(),NOW)
        with self.assertRaises(ValueError):g.submit(self.plan(g,'b'),quotes(),NOW)   # wedged: no blind retry
        changes=g.reconcile(NOW+timedelta(seconds=5))
        self.assertEqual([c[1:] for c in changes],[('uncertain','filled')])
        b.post_error=None;self.assertEqual(g.submit(self.plan(g,'c'),quotes(),NOW)['status'],'filled')
    def test_reconcile_only_declares_not_found_after_settle_window(self):
        g,b=self.live(FakeBroker(post_error=TimeoutError('?')))
        with self.assertRaises(TimeoutError):g.submit(self.plan(g),quotes(),NOW)
        self.assertEqual(g.reconcile(NOW+timedelta(seconds=30)),[])        # could still be in flight
        self.assertEqual([c[2] for c in g.reconcile(NOW+timedelta(seconds=200))],['not_found'])
    def test_reconcile_never_clears_an_unprotected_open_trade(self):
        def lookup(path):return {'order':dict(state='FILLED',tradeOpenedID='42')}
        g,b=self.live(FakeBroker(post_error=TimeoutError('?'),order_lookup=lookup))
        with self.assertRaises(TimeoutError):g.submit(self.plan(g),quotes(),NOW)
        orig=b.__call__
        def naked(method,path,payload=None):
            if method=='GET' and '/trades/' in path:return dict(trade=dict(state='OPEN'))
            return orig(method,path,payload)
        g.send=naked
        self.assertEqual([c[2] for c in g.reconcile(NOW)],['filled_unverified_protection'])
        with self.assertRaises(ValueError):g.submit(self.plan(g,'z'),quotes(),NOW)

    def test_flatten_works_while_stopped_and_without_arming(self):
        open(self.stop,'w').close()
        g=LiveOrders(self.db,'live','tok-123456',ACCT,None,None,b:=FakeBroker(),{},require_arm=False)
        out=g.flatten()
        self.assertEqual((out['closed'],out['cancelled'],out['errors']),(['7','8'],['9'],[]))
        with self.assertRaises(PermissionError):g.submit(g.plan('EUR_USD','buy','x',quotes(),10000,NOW),quotes(),NOW)
    def test_flatten_single_instrument_leaves_others_and_pending(self):
        g=LiveOrders(self.db,'live','tok-123456',ACCT,None,None,FakeBroker(),{},require_arm=False)
        out=g.flatten('EUR_USD');self.assertEqual((out['closed'],out['cancelled']),(['7'],[]))

if __name__=='__main__':unittest.main()
