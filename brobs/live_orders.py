"""Real-money-capable OANDA execution gateway. DISARMED BY DEFAULT.

It reuses the practice gateway's order plan (market FOK entry, broker-side stop
and target, price bound), its "persist *uncertain* before sending, never blind
retry" journal rule, and adds the pieces the readiness audit listed as missing:

* an explicit arming phrase (live only), an operator stop file, hard per-order
  size, orders-per-day and daily-loss ceilings;
* ``reconcile()``: resolves ``uncertain`` attempts by asking the broker, never by
  guessing, so one network timeout no longer wedges the account forever;
* ``flatten()``: an emergency exit that closes open trades and cancels pending
  orders. It is risk-reducing, so it does not require arming or the stop file.

NOT VERIFIED AGAINST A REAL BROKER: no credentialed OANDA session was available
when this was written; everything is fixture-tested. Run on a PRACTICE account
first. This code cannot make a strategy profitable; BROBS has no demonstrated edge.
"""
import json,math,os,re,sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime,timezone
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request,build_opener
from .broker_readiness import BASES
from .fx import PAIRS,validate_quotes,utc
from .practice_orders import entry_plan,NoRedirect

ARM_PHRASE='I ACCEPT THAT BROBS HAS NO PROVEN EDGE AND I MAY LOSE ALL FUNDS IN THIS ACCOUNT'
BLOCKING=('uncertain','filled_unverified_protection')
NON_COUNTING=('rejected','cancelled','not_found')
ACCOUNT=re.compile(r'[A-Za-z0-9-]{5,64}')
IDENT=re.compile(r'brobs-[a-f0-9]{40}')
DIGITS=re.compile(r'[0-9]{1,20}')

@dataclass(frozen=True)
class LiveLimits:
    max_units:int=1000
    max_orders_per_day:int=3
    max_daily_loss_fraction:float=.02
    def __post_init__(self):
        ints=(self.max_units,self.max_orders_per_day)
        if any(isinstance(v,bool) or not isinstance(v,int) for v in ints):raise ValueError('Limits must be integers')
        if not 1<=self.max_units<=100000 or not 1<=self.max_orders_per_day<=20:raise ValueError('Limit outside hard ceiling')
        if not math.isfinite(self.max_daily_loss_fraction) or not 0<self.max_daily_loss_fraction<=.05:raise ValueError('Daily loss limit must be in (0, 5%]')

def protected(trade):
    return trade.get('state')=='OPEN' and all(trade.get(k,{}).get('state')=='PENDING' for k in ('stopLossOrder','takeProfitOrder'))

class LiveOrders:
    def __init__(self,path,environment='practice',token=None,account=None,limits=None,stop_file=None,transport=None,environ=None,require_arm=True):
        if environment not in BASES:raise ValueError('Unknown environment')
        env=os.environ if environ is None else environ
        prefix='OANDA_LIVE' if environment=='live' else 'OANDA_PRACTICE'
        self.environment=environment;self.base=BASES[environment]
        self.token=token if token is not None else env.get(prefix+'_TOKEN','')
        self.account=account if account is not None else env.get(prefix+'_ACCOUNT','')
        self.limits=limits or LiveLimits()
        self.stop_file=stop_file if stop_file is not None else env.get('BROBS_LIVE_STOP_FILE')
        self.armed=environment=='practice' or env.get('BROBS_LIVE_ARM')==ARM_PHRASE
        if require_arm and not self.armed:
            raise PermissionError('Live trading is disarmed. Set BROBS_LIVE_ARM to the exact acknowledgement in docs/LIVE_TRADING.md.')
        if environment=='live' and require_arm and not self.stop_file:
            raise ValueError('Live trading requires BROBS_LIVE_STOP_FILE (operator kill switch path)')
        if not self.token or not ACCOUNT.fullmatch(self.account):raise ValueError('Broker credentials required')
        self.path=path;self.send=transport or self._http
        with self._tx() as db:
            db.execute('CREATE TABLE IF NOT EXISTS live_binding (account TEXT PRIMARY KEY, environment TEXT)')
            binding=db.execute('SELECT account,environment FROM live_binding').fetchall()
            if binding and binding!=[(self.account,environment)]:raise ValueError('Journal belongs to another account/environment')
            db.execute('INSERT OR IGNORE INTO live_binding VALUES (?,?)',(self.account,environment))
            db.execute('CREATE TABLE IF NOT EXISTS live_attempts (id TEXT PRIMARY KEY, status TEXT, payload TEXT, response TEXT, created_at TEXT, day TEXT)')
            db.execute('CREATE TABLE IF NOT EXISTS live_days (day TEXT PRIMARY KEY, start_nav REAL)')

    @contextmanager
    def _tx(self):
        db=sqlite3.connect(self.path,timeout=30,isolation_level=None)
        try:
            db.execute('BEGIN IMMEDIATE');yield db;db.execute('COMMIT')
        except BaseException:
            try:db.execute('ROLLBACK')
            except sqlite3.Error:pass
            raise
        finally:db.close()

    def _http(self,method,path,payload=None):
        request=Request(self.base+path,data=json.dumps(payload,allow_nan=False).encode() if payload is not None else None,
            headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json','Accept':'application/json'},method=method)
        try:
            with build_opener(NoRedirect()).open(request,timeout=15) as response:raw=response.read(200001)
        except HTTPError as error:
            if error.code==404:return {'_status':404}
            raise
        if len(raw)>200000:raise ValueError('Oversized broker response')
        return json.loads(raw)

    def quotes(self,instruments):
        if not instruments or any(p not in PAIRS for p in instruments):raise ValueError('Unsupported instrument')
        payload=self.send('GET',f'/v3/accounts/{self.account}/pricing?'+urlencode({'instruments':','.join(instruments)}))
        result={}
        for item in payload.get('prices',[]):
            symbol=item['instrument']
            if symbol not in instruments:continue
            if not item.get('bids') or not item.get('asks'):raise ValueError('Missing executable bid/ask')
            result[symbol]=dict(bid=float(item['bids'][0]['price']),ask=float(item['asks'][0]['price']),timestamp=item['time'],tradeable=item.get('status')=='tradeable')
        if set(result)!=set(instruments):raise ValueError('Missing instrument quotes')
        return result

    def plan(self,symbol,action,signal_id,quotes,capital,now,config=None):
        built=entry_plan(symbol,action,signal_id,quotes,capital,now,config)
        order=built['order'];built['environment']=self.environment
        order['clientExtensions']['tag']='BROBS_LIVE' if self.environment=='live' else 'BROBS_PRACTICE'
        units=int(order['units'])
        if abs(units)>self.limits.max_units:order['units']=str((1 if units>0 else -1)*self.limits.max_units)
        return built

    def submit(self,plan,quotes,now,config=None):
        if not self.armed:raise PermissionError('Gateway is disarmed')
        if plan.get('environment')!=self.environment:raise ValueError('Plan environment mismatch')
        if self.stop_file and os.path.exists(self.stop_file):raise PermissionError('Operator stop file present: new entries blocked')
        if not 0<=(utc(now)-utc(plan['created_at'])).total_seconds()<=30:raise ValueError('Entry plan expired')
        order=plan['order'];ident=order['clientExtensions']['id']
        if not IDENT.fullmatch(ident):raise ValueError('Invalid identifier')
        day=utc(now).date().isoformat()
        with self._tx() as db:
            if db.execute('SELECT 1 FROM live_attempts WHERE status IN (?,?)',BLOCKING).fetchone():
                raise ValueError('Uncertain submission/protection: run reconcile or inspect the broker before continuing')
            if db.execute('SELECT 1 FROM live_attempts WHERE id=?',(ident,)).fetchone():raise ValueError('Already attempted; no automatic retry')
            placed=db.execute('SELECT COUNT(*) FROM live_attempts WHERE day=? AND status NOT IN (?,?,?)',(day,)+NON_COUNTING).fetchone()[0]
            if placed>=self.limits.max_orders_per_day:raise PermissionError('Daily order limit reached')
            account=self.send('GET',f'/v3/accounts/{self.account}/summary')['account']
            if account.get('currency')!='USD' or account.get('mt4AccountID'):raise ValueError('USD non-MT4 account required')
            if int(account['openTradeCount'])!=0 or int(account['pendingOrderCount'])!=0:raise ValueError('Use a dedicated account with no open trades or pending orders')
            nav=float(account['NAV']);cap=float(plan['capital_cap'])
            if not math.isfinite(nav) or nav<=0 or not math.isfinite(cap) or cap<=0:raise ValueError('Invalid account balance')
            row=db.execute('SELECT start_nav FROM live_days WHERE day=?',(day,)).fetchone()
            start=row[0] if row else nav
            if not row:db.execute('INSERT INTO live_days VALUES (?,?)',(day,nav))
            if nav<=start*(1-self.limits.max_daily_loss_fraction):raise PermissionError('Daily loss limit reached: no new entries today')
            rebuilt=self.plan(order['instrument'],'buy' if int(order['units'])>0 else 'sell','validation',quotes,min(nav,cap),now,config)
            expected=rebuilt['order'];expected['clientExtensions']['id']=ident
            if order!=expected:raise ValueError('Order differs from current risk/quote validation')
            # Persist uncertainty BEFORE transport: a crash or timeout never permits resubmission.
            db.execute('INSERT INTO live_attempts VALUES (?,?,?,?,?,?)',(ident,'uncertain',json.dumps(plan,allow_nan=False),None,utc(now).isoformat(),day))
        response=self.send('POST',f'/v3/accounts/{self.account}/orders',dict(order=order))
        status='filled' if 'orderFillTransaction' in response else 'cancelled' if 'orderCancelTransaction' in response else 'rejected' if 'orderRejectTransaction' in response else 'uncertain'
        if status=='filled':
            status='filled_unverified_protection'
            trade_id=response['orderFillTransaction'].get('tradeOpened',{}).get('tradeID')
            if isinstance(trade_id,str) and DIGITS.fullmatch(trade_id):
                try:status=self._verify_trade(trade_id,status)
                except Exception:pass  # known fill, unverifiable bracket: stays blocking
        with self._tx() as db:
            db.execute('UPDATE live_attempts SET status=?,response=? WHERE id=?',(status,json.dumps(response,allow_nan=False),ident))
        return dict(environment=self.environment,status=status,response=response)

    def _verify_trade(self,trade_id,default):
        trade=self.send('GET',f'/v3/accounts/{self.account}/trades/{trade_id}')['trade']
        if trade.get('state')=='CLOSED':return 'closed'
        return 'filled' if protected(trade) else default

    def reconcile(self,now=None,settle_seconds=120):
        """Resolve blocking attempts from broker truth. Returns [(id, old, new)]."""
        now=utc(now or datetime.now(timezone.utc));changes=[]
        with self._tx() as db:
            rows=db.execute('SELECT id,status,created_at FROM live_attempts WHERE status IN (?,?)',BLOCKING).fetchall()
        for ident,old,created in rows:
            new=old
            order=self.send('GET',f'/v3/accounts/{self.account}/orders/@{ident}')
            if order.get('_status')==404:
                if (now-utc(created)).total_seconds()>=settle_seconds:new='not_found'
            else:
                body=order.get('order',{});state=body.get('state')
                if state=='CANCELLED':new='cancelled'
                elif state=='FILLED':
                    trade_id=body.get('tradeOpenedID')
                    if not trade_id and body.get('fillingTransactionID'):
                        filled=self.send('GET',f"/v3/accounts/{self.account}/transactions/{body['fillingTransactionID']}")
                        trade_id=filled.get('transaction',{}).get('tradeOpened',{}).get('tradeID')
                    if isinstance(trade_id,str) and DIGITS.fullmatch(trade_id):new=self._verify_trade(trade_id,'filled_unverified_protection')
                    else:new='filled_unverified_protection'
            if new!=old:
                with self._tx() as db:db.execute('UPDATE live_attempts SET status=? WHERE id=?',(new,ident))
                changes.append((ident,old,new))
        return changes

    def flatten(self,instrument=None):
        """Emergency exit: close open trades (optionally one pair) and cancel pending orders."""
        if instrument is not None and instrument not in PAIRS:raise ValueError('Unsupported instrument')
        out=dict(closed=[],cancelled=[],errors=[])
        for trade in self.send('GET',f'/v3/accounts/{self.account}/openTrades').get('trades',[]):
            tid=str(trade.get('id',''))
            if not DIGITS.fullmatch(tid) or (instrument and trade.get('instrument')!=instrument):continue
            try:self.send('PUT',f'/v3/accounts/{self.account}/trades/{tid}/close',{'units':'ALL'});out['closed'].append(tid)
            except Exception as error:out['errors'].append(f'close {tid}: {type(error).__name__}')
        if instrument is None:
            for pending in self.send('GET',f'/v3/accounts/{self.account}/pendingOrders').get('orders',[]):
                oid=str(pending.get('id',''))
                if not DIGITS.fullmatch(oid):continue
                try:self.send('PUT',f'/v3/accounts/{self.account}/orders/{oid}/cancel');out['cancelled'].append(oid)
                except Exception as error:out['errors'].append(f'cancel {oid}: {type(error).__name__}')
        return out

def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description='BROBS broker gateway tools (reconcile / flatten / status). Never places entries.')
    parser.add_argument('command',choices=('status','reconcile','flatten'))
    parser.add_argument('--environment',choices=tuple(BASES),default='practice')
    parser.add_argument('--journal',default='live_orders.db')
    parser.add_argument('--instrument')
    args=parser.parse_args(argv)
    gateway=LiveOrders(args.journal,args.environment,require_arm=False)
    if args.command=='reconcile':print(json.dumps(gateway.reconcile(),indent=2))
    elif args.command=='flatten':print(json.dumps(gateway.flatten(args.instrument),indent=2))
    else:
        summary=gateway.send('GET',f'/v3/accounts/{gateway.account}/summary')['account']
        print(json.dumps({k:summary.get(k) for k in ('currency','balance','NAV','openTradeCount','pendingOrderCount')},indent=2))

if __name__=='__main__':main()
