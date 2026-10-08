"""Read-only market-data clients. No order API, public webhooks or real-money code."""
import json
import math
import os
import urllib.parse
import urllib.request
from datetime import datetime,timedelta,timezone
from .fx import utc
from .market_book import STOCKS,CRYPTO


def request_json(url,headers=None):
    request=urllib.request.Request(url,headers={'Cache-Control':'no-cache', **(headers or {})},method='GET')
    with urllib.request.urlopen(request,timeout=15) as response:
        raw=response.read(2000001)
    if len(raw)>2000000:raise ValueError('Oversized market response')
    return json.loads(raw)


def validate_bars(rows):
    if not rows:raise ValueError('No completed bars')
    previous=None
    for row in rows:
        stamp=utc(row['timestamp'])
        if previous and stamp<=previous:raise ValueError('Unordered bars')
        previous=stamp
        values=[row[k] for k in ('open','high','low','close','volume')]
        if any(not math.isfinite(v) or v<0 for v in values) or min(values[:4])<=0 or row['low']>min(row['open'],row['close']) or row['high']<max(row['open'],row['close']):raise ValueError('Invalid OHLCV')
    return rows


class BinanceData:
    source='Binance public spot snapshots — LOCAL USDT PAPER, NO EXCHANGE ORDERS'
    market='crypto'
    def __init__(self,transport=None):self.transport=transport or self._get
    def _get(self,path):return request_json('https://data-api.binance.vision'+path)
    def market_open(self):return True
    def candles(self,symbol,now=None):
        if symbol not in CRYPTO:raise ValueError('Unsupported crypto pair')
        now=utc(now or datetime.now(timezone.utc))
        raw=self.transport('/api/v3/klines?'+urllib.parse.urlencode(dict(symbol=symbol.replace('_',''),interval='1h',limit=500)))
        rows=[dict(timestamp=datetime.fromtimestamp(v[0]/1000,timezone.utc),open=float(v[1]),high=float(v[2]),low=float(v[3]),close=float(v[4]),volume=float(v[5])) for v in raw if datetime.fromtimestamp(v[6]/1000,timezone.utc)<now]
        return validate_bars(rows)
    def quotes(self,symbols):
        at=datetime.fromtimestamp(self.transport('/api/v3/time')['serverTime']/1000,timezone.utc)
        quotes={}
        for symbol in symbols:
            if symbol not in CRYPTO:raise ValueError('Unsupported crypto pair')
            q=self.transport('/api/v3/ticker/bookTicker?symbol='+symbol.replace('_',''))
            if q.get('symbol')!=symbol.replace('_',''):raise ValueError('Wrong quote symbol')
            quotes[symbol]=dict(bid=float(q['bidPrice']),ask=float(q['askPrice']),timestamp=at.isoformat(),tradeable=float(q['bidQty'])>0 and float(q['askQty'])>0)
        # bookTicker does not carry an exchange event timestamp. Conservatively use
        # server time fetched BEFORE the snapshot; subsequent delays can make it stale.
        return quotes


class AlpacaData:
    source='Alpaca IEX snapshots — LOCAL USD STOCK PAPER, NO BROKER ORDERS'
    market='stock'
    def __init__(self,key=None,secret=None,transport=None):
        self.key=key or os.getenv('ALPACA_PAPER_KEY');self.secret=secret or os.getenv('ALPACA_PAPER_SECRET')
        if transport is None and (not self.key or not self.secret):raise ValueError('Set local Alpaca paper data credentials')
        self.transport=transport or self._get
    def _get(self,path):
        if path=='/v2/clock':base='https://paper-api.alpaca.markets'
        elif path.startswith('/v2/stocks/'):base='https://data.alpaca.markets'
        else:raise ValueError('Only clock/stock data requests enabled')
        return request_json(base+path,{'APCA-API-KEY-ID':self.key,'APCA-API-SECRET-KEY':self.secret})
    def market_open(self):return self.transport('/v2/clock').get('is_open') is True
    def candles(self,symbol,now=None):
        if symbol not in STOCKS:raise ValueError('Unsupported stock')
        now=utc(now or datetime.now(timezone.utc))
        params=dict(timeframe='1Hour',start=(now-timedelta(days=90)).isoformat(),end=now.isoformat(),limit=10000,sort='asc',feed='iex',adjustment='all')
        raw=self.transport(f'/v2/stocks/{symbol}/bars?'+urllib.parse.urlencode(params))
        if raw.get('next_page_token'):raise ValueError('History pagination required; refusing incomplete window')
        rows=[dict(timestamp=utc(v['t']),open=float(v['o']),high=float(v['h']),low=float(v['l']),close=float(v['c']),volume=float(v['v'])) for v in raw.get('bars',[]) if utc(v['t'])+timedelta(hours=1)<=now]
        return validate_bars(rows[-500:])
    def quotes(self,symbols):
        quotes={}
        for symbol in symbols:
            if symbol not in STOCKS:raise ValueError('Unsupported stock')
            q=self.transport(f'/v2/stocks/{symbol}/quotes/latest?feed=iex')['quote']
            quotes[symbol]=dict(bid=float(q['bp']),ask=float(q['ap']),timestamp=q['t'],tradeable=float(q.get('bs',0))>0 and float(q.get('as',0))>0)
        return quotes
