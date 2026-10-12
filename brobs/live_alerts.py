"""TradingView webhook -> BROBS broker gateway (forex). Practice by default; live only when armed.

TradingView alerts carry one price, not a bid/ask, so this receiver NEVER trusts the
alert for execution: it pulls fresh executable quotes from the broker, rejects alerts
whose price disagrees with them, and sends the order through ``LiveOrders`` (bracketed,
journaled, rate-limited, stop-file aware).

Dedupe is durable and claimed BEFORE any broker contact (UNIQUE constraint), so a
TradingView retry, a restart or two simultaneous deliveries can never place two orders.
A failed event is consumed, not retried: for real money, failing closed beats re-firing.
"""
import hmac,json,os,sqlite3,threading
from contextlib import closing
from datetime import datetime,timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from .fx import PAIRS,FXConfig
from .live_orders import LiveOrders,LiveLimits

class LiveAlertService:
    def __init__(self,secret,gateway,journal_path,capital,max_price_deviation=.003,clock=None,config=None):
        if not isinstance(secret,str) or len(secret)<24:raise ValueError('Configure a random secret with at least 24 characters')
        if not isinstance(capital,(int,float)) or isinstance(capital,bool) or not 0<capital<=1e9:raise ValueError('Invalid capital cap')
        if not 0<max_price_deviation<=.05:raise ValueError('Invalid price deviation limit')
        self.secret=secret;self.gateway=gateway;self.capital=float(capital);self.max_dev=max_price_deviation
        self.clock=clock or (lambda:datetime.now(timezone.utc));self.config=config;self.path=journal_path;self.lock=threading.Lock()
        with closing(sqlite3.connect(journal_path)) as db,db:
            db.execute('CREATE TABLE IF NOT EXISTS live_events (event_id TEXT PRIMARY KEY, received_at TEXT, outcome TEXT)')
    def _claim(self,event_id):
        with closing(sqlite3.connect(self.path,timeout=30)) as db:
            try:
                with db:db.execute('INSERT INTO live_events VALUES (?,?,NULL)',(event_id,self.clock().isoformat()))
                return True
            except sqlite3.IntegrityError:return False
    def _outcome(self,event_id,text):
        with closing(sqlite3.connect(self.path,timeout=30)) as db,db:
            db.execute('UPDATE live_events SET outcome=? WHERE event_id=?',(text[:200],event_id))
    def handle(self,payload):
        if not isinstance(payload,dict):raise ValueError('JSON object required')
        if not hmac.compare_digest(str(payload.get('secret','')),self.secret):raise PermissionError('Unauthorized')
        event_id=payload.get('event_id')
        if not isinstance(event_id,str) or not 1<=len(event_id)<=128:raise ValueError('event_id required')
        symbol=payload.get('symbol');action=payload.get('action')
        if symbol not in PAIRS or action not in ('buy','sell','close'):raise ValueError('Invalid symbol or action')
        if payload.get('market','forex')!='forex':raise ValueError('Only forex is supported by the broker gateway')
        if not self._claim(event_id):return {'status':'duplicate'}
        try:
            result=self._execute(event_id,symbol,action,payload)
        except Exception as error:
            self._outcome(event_id,'error:'+type(error).__name__+':'+str(error));raise
        self._outcome(event_id,result['status']);return result
    def _execute(self,event_id,symbol,action,payload):
        if action=='close':
            return {'status':'flattened',**self.gateway.flatten(symbol)}
        now=self.clock();quotes=self.gateway.quotes([symbol])
        if 'price' in payload:
            price=float(payload['price']);q=quotes[symbol];mid=(q['bid']+q['ask'])/2
            if not 0<price<1e6 or abs(price-mid)/mid>self.max_dev:raise ValueError('Alert price disagrees with broker quote')
        plan=self.gateway.plan(symbol,action,event_id,quotes,self.capital,now,self.config)
        with self.lock:result=self.gateway.submit(plan,quotes,now,self.config)
        return {'status':result['status'],'environment':result['environment'],'symbol':symbol,'action':action}

def serve(port=8768):
    environment=os.environ.get('BROBS_LIVE_ENVIRONMENT','practice')
    capital=float(os.environ.get('BROBS_LIVE_CAPITAL','0'))
    journal=os.environ.get('BROBS_LIVE_JOURNAL','live_orders.db')
    limits=LiveLimits(int(os.environ.get('BROBS_LIVE_MAX_UNITS','1000')),int(os.environ.get('BROBS_LIVE_MAX_ORDERS_PER_DAY','3')),
        float(os.environ.get('BROBS_LIVE_MAX_DAILY_LOSS','0.02')))
    gateway=LiveOrders(journal,environment,limits=limits)
    service=LiveAlertService(os.environ.get('BROBS_ALERT_SECRET',''),gateway,journal,capital)
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path!='/alert':self.send_error(404);return
            try:length=int(self.headers.get('Content-Length','0'))
            except ValueError:self.send_error(400);return
            if not 0<length<=4096:self.send_error(413);return
            try:result=service.handle(json.loads(self.rfile.read(length)));status=200
            except PermissionError as e:
                result={'error':'unauthorized' if str(e)=='Unauthorized' else 'blocked','detail':str(e)} ;status=401 if str(e)=='Unauthorized' else 409
            except (ValueError,TypeError,KeyError,json.JSONDecodeError) as e:result={'error':'rejected','detail':str(e)[:120]};status=400
            except Exception as e:result={'error':'broker_error','detail':type(e).__name__};status=502
            body=json.dumps(result).encode()
            self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def log_message(self,*args):pass
    print(f'BROBS broker webhook on 127.0.0.1:{port} environment={environment.upper()} capital_cap={capital} limits={limits}')
    if environment=='live':print('*** LIVE: REAL MONEY. Create the stop file to block new entries; `python -m brobs.live_orders flatten --environment live` closes everything. ***')
    ThreadingHTTPServer(('127.0.0.1',port),Handler).serve_forever()

if __name__=='__main__':serve()
