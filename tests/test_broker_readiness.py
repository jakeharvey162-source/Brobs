import tempfile,sqlite3,unittest
from pathlib import Path
from brobs.broker_readiness import OandaReadiness,BASES
def ready_account():
 return dict(account=dict(currency='USD',NAV='10000',balance='10000',
                          openTradeCount=0,pendingOrderCount=0))
class BrokerReadinessTests(unittest.TestCase):
 def transport(self,summary=None,trades=None,orders=None):
  calls=[]
  def send(path):
   calls.append(path)
   if path.endswith('/summary'):return summary or ready_account()
   if path.endswith('/openTrades'):return dict(trades=trades if trades is not None else [])
   if path.endswith('/pendingOrders'):return dict(orders=orders if orders is not None else [])
   raise AssertionError('Unexpected broker action: '+path)
  return send,calls
 def test_practice_and_live_audit_never_posts_an_order(self):
  for env in ('practice','live'):
   with self.subTest(env=env):
    feed,calls=self.transport()
    result=OandaReadiness(env,'fake-token','101-123-456',feed).audit()
    self.assertTrue(result['audit_passed'])
    self.assertFalse(result['market_order_submission_enabled'])
    self.assertFalse(result['real_money_execution_enabled'])
    self.assertEqual(len(calls),3)
    self.assertTrue(all(x.startswith('/v3/accounts/101-123-456/') for x in calls))
 def test_live_practice_hostname_separation(self):
  self.assertEqual(BASES['live'],'https://api-fxtrade.oanda.com')
  self.assertEqual(BASES['practice'],'https://api-fxpractice.oanda.com')
 def test_live_account_with_existing_trades_is_not_approved(self):
  feed,_=self.transport(summary=dict(account=dict(currency='USD',NAV='10000',balance='10000',openTradeCount=1,pendingOrderCount=0)),
                        trades=[dict(id='101',state='OPEN')])
  result=OandaReadiness('live','token','101-123-456',feed).audit()
  self.assertFalse(result['audit_passed'])
  self.assertTrue(any('open broker trades' in x for x in result['blockers']))
 def test_disagreements_and_nonusd_account_block(self):
  bad=dict(account=dict(currency='ZAR',NAV='10000',balance='10000',openTradeCount=2,pendingOrderCount=0))
  feed,_=self.transport(summary=bad)
  result=OandaReadiness('practice','token','101-123-456',feed).audit()
  self.assertFalse(result['audit_passed'])
  self.assertTrue(any('count disagrees' in x for x in result['blockers']))
 def test_journal_uncertainty_blocks(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'practice.db'
   with sqlite3.connect(path) as db:
    db.execute('CREATE TABLE broker_binding(account TEXT PRIMARY KEY)')
    db.execute('INSERT INTO broker_binding VALUES (?)',('101-123-456',))
    db.execute('CREATE TABLE broker_attempts (id TEXT, status TEXT, payload TEXT, response TEXT)')
    db.execute('INSERT INTO broker_attempts VALUES (?,?,?,?)',('attempt','uncertain','{}',None))
   feed,_=self.transport()
   r=OandaReadiness('practice','token','101-123-456',feed).audit(path)
   self.assertFalse(r['audit_passed'])
   self.assertTrue(any('unresolved' in x for x in r['blockers']))
 def test_missing_credentials_do_not_work(self):
  with self.assertRaises(ValueError):OandaReadiness('live','','bad!')
  with self.assertRaises(ValueError):OandaReadiness('invalid','token','101-123-456')
