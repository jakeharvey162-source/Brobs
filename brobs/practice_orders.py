"""OANDA practice entry gateway. Broker brackets; durable no-blind-retry journal.

Separate from the local paper ledger. No live host or real-account execution.
"""
import hashlib,json,math,os,re,sqlite3
from datetime import datetime,timezone
from urllib.request import Request,build_opener,HTTPRedirectHandler
from .fx import FXConfig,PAIRS,validate_quotes,utc
from .oanda_practice import BASE

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValueError('Broker redirect refused')

def entry_plan(symbol,action,signal_id,quotes,capital,now,config=None):
    cfg=config or FXConfig(capital=capital)
    if symbol not in PAIRS or action not in ('buy','sell') or not isinstance(signal_id,str) or not 0<len(signal_id)<=200:
        raise ValueError('Invalid entry proposal')
    validate_quotes(quotes,now,cfg)
    if not math.isfinite(capital) or capital<=0:raise ValueError('Invalid paper capital')
    q=quotes[symbol]
    if (q['ask']-q['bid'])/q['bid']>cfg.max_spread_fraction:raise ValueError('Spread exceeds limit')
    sign=1 if action=='buy' else -1
    entry=q['ask'] if sign>0 else q['bid']
    # Include a price-bound reserve and round whole currency units down.
    bound=entry*(1+sign*cfg.slippage_fraction)
    reserve=max(entry,bound)
    risk=reserve*(cfg.stop_fraction+2*cfg.commission_fraction+cfg.slippage_fraction)
    units=math.floor(min(capital*cfg.risk_fraction/risk,capital*cfg.max_notional_fraction/reserve))
    if units<1:raise ValueError('Insufficient units')
    stop=bound*(1-sign*cfg.stop_fraction);target=bound*(1+sign*cfg.stop_fraction*cfg.reward_risk)
    ident='brobs-'+hashlib.sha256((symbol+':'+signal_id).encode()).hexdigest()[:40]
    order=dict(type='MARKET',instrument=symbol,units=str(sign*units),timeInForce='FOK',positionFill='OPEN_ONLY',
        priceBound=f'{bound:.5f}',clientExtensions=dict(id=ident,tag='BROBS_PRACTICE'),
        stopLossOnFill=dict(price=f'{stop:.5f}',timeInForce='GTC'),takeProfitOnFill=dict(price=f'{target:.5f}',timeInForce='GTC'))
    return dict(environment='practice',created_at=utc(now).isoformat(),capital_cap=capital,order=order)

class PracticeOrders:
    def __init__(self,path,token=None,account=None,transport=None):
        self.token=token if token is not None else os.getenv('OANDA_PRACTICE_TOKEN','')
        self.account=account if account is not None else os.getenv('OANDA_PRACTICE_ACCOUNT','')
        if not self.token or not re.fullmatch(r'[A-Za-z0-9-]{5,64}',self.account):raise ValueError('Practice credentials required')
        self.path=path;self.send=transport or self._http
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS broker_binding (account TEXT PRIMARY KEY)')
            binding=db.execute('SELECT account FROM broker_binding').fetchall()
            if binding and binding!=[(self.account,)]:raise ValueError('Journal belongs to another account')
            db.execute('INSERT OR IGNORE INTO broker_binding VALUES (?)',(self.account,))
            db.execute('CREATE TABLE IF NOT EXISTS broker_attempts (id TEXT PRIMARY KEY, status TEXT, payload TEXT, response TEXT)')
    def _http(self,method,path,payload=None):
        request=Request(BASE+path,data=json.dumps(payload,allow_nan=False).encode() if payload else None,
            headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json'},method=method)
        with build_opener(NoRedirect()).open(request,timeout=15) as response:
            raw=response.read(200001)
        if len(raw)>200000:raise ValueError('Oversized broker response')
        return json.loads(raw)
    def submit(self,plan,quotes,now,config=None):
        # Rebuild all prices/units from current quotes; callers cannot inject raw orders.
        if plan.get('environment')!='practice':raise ValueError('Practice only')
        age=(utc(now)-utc(plan['created_at'])).total_seconds()
        if not 0<=age<=30:raise ValueError('Entry plan expired')
        order=plan['order'];ident=order['clientExtensions']['id']
        if not re.fullmatch(r'brobs-[a-f0-9]{40}',ident):raise ValueError('Invalid identifier')
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute("SELECT 1 FROM broker_attempts WHERE status IN ('uncertain','filled_unverified_protection')").fetchone():raise ValueError('Uncertain submission/protection: inspect broker before continuing')
            if db.execute('SELECT 1 FROM broker_attempts WHERE id=?',(ident,)).fetchone():raise ValueError('Already attempted; no automatic retry')
            account=self.send('GET',f'/v3/accounts/{self.account}/summary')['account']
            if account.get('currency')!='USD' or account.get('mt4AccountID'):raise ValueError('USD non-MT4 practice account required')
            if int(account['openTradeCount'])!=0 or int(account['pendingOrderCount'])!=0:raise ValueError('Use an empty dedicated practice account')
            nav=float(account['NAV']);cap=float(plan['capital_cap'])
            if not math.isfinite(nav) or nav<=0 or not math.isfinite(cap) or cap<=0:raise ValueError('Invalid account balance')
            rebuilt=entry_plan(order['instrument'],'buy' if int(order['units'])>0 else 'sell','validation',quotes,min(nav,cap),now,config)
            expected=rebuilt['order'];expected['clientExtensions']['id']=ident
            if order!=expected:raise ValueError('Order differs from current risk/quote validation')
            # Persist uncertainty BEFORE transport. A crash or timeout never permits resubmission.
            db.execute('INSERT INTO broker_attempts VALUES (?,?,?,?)',(ident,'uncertain',json.dumps(plan,allow_nan=False),None))
        response=self.send('POST',f'/v3/accounts/{self.account}/orders',dict(order=order))
        status='filled' if 'orderFillTransaction' in response else 'cancelled' if 'orderCancelTransaction' in response else 'rejected' if 'orderRejectTransaction' in response else 'uncertain'
        if status=='filled':
            # A requested bracket is not proof it exists on the broker trade.
            status='filled_unverified_protection'
            trade_id=response['orderFillTransaction'].get('tradeOpened',{}).get('tradeID')
            if isinstance(trade_id,str) and trade_id.isdigit():
                trade=self.send('GET',f'/v3/accounts/{self.account}/trades/{trade_id}')['trade']
                if trade.get('state')=='CLOSED':status='closed'
                elif trade.get('state')=='OPEN' and all(trade.get(k,{}).get('state')=='PENDING' for k in ('stopLossOrder','takeProfitOrder')):
                    status='filled'
        with sqlite3.connect(self.path) as db:
            db.execute('UPDATE broker_attempts SET status=?,response=? WHERE id=?',(status,json.dumps(response,allow_nan=False),ident))
        return dict(environment='practice',status=status,response=response)
