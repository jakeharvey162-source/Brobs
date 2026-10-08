"""OANDA v20 PRACTICE read-only adapter. Never uses live hostname or order endpoints."""
import json,os,re
from math import isfinite
from urllib.request import Request,urlopen
from urllib.parse import urlencode,quote
from datetime import datetime,timezone

BASE="https://api-fxpractice.oanda.com"
PAIR=re.compile(r"^[A-Z]{3}_[A-Z]{3}$")
class PracticeData:
    def __init__(self,token=None,account=None,transport=None):
        self.token=token if token is not None else os.getenv("OANDA_PRACTICE_TOKEN","")
        self.account=account if account is not None else os.getenv("OANDA_PRACTICE_ACCOUNT","")
        self.transport=transport or self._http
        if not self.token or not self.account:raise ValueError("Practice account and token required")
    def _http(self,path):
        req=Request(BASE+path,headers={"Authorization":"Bearer "+self.token,"Accept":"application/json"},method="GET")
        with urlopen(req,timeout=12) as response:return json.load(response)
    def candles(self,instrument="EUR_USD",granularity="H1",count=200):
        if not PAIR.fullmatch(instrument):raise ValueError("Invalid currency pair")
        if granularity not in ("M5","M15","H1","H4","D"):raise ValueError("Unsupported granularity")
        if not 30<=count<=5000:raise ValueError("Invalid count")
        path="/v3/instruments/"+quote(instrument)+"/candles?"+urlencode({"price":"M","granularity":granularity,"count":count})
        payload=self.transport(path)
        rows=[]
        for item in payload.get("candles",[]):
            if not item.get("complete"):continue
            mid=item["mid"]
            row={"timestamp":datetime.fromisoformat(item["time"].replace("Z","+00:00")),"open":float(mid["o"]),"high":float(mid["h"]),"low":float(mid["l"]),"close":float(mid["c"]),"volume":float(item.get("volume",0))}
            if any(not isfinite(row[k]) or row[k]<=0 for k in ("open","high","low","close")) or not isfinite(row["volume"]) or row["volume"]<0:raise ValueError("Invalid candle")
            if row["low"]>min(row["open"],row["close"]) or row["high"]<max(row["open"],row["close"]):raise ValueError("Inconsistent candle range")
            if rows and row["timestamp"]<=rows[-1]["timestamp"]:raise ValueError("Out-of-order candles")
            rows.append(row)
        if len(rows)<30:raise ValueError("Insufficient completed candles")
        return rows
    def quotes(self,instruments=("EUR_USD",)):
        if not instruments or any(not PAIR.fullmatch(p) for p in instruments):raise ValueError("Invalid currency pairs")
        if not re.fullmatch(r"[A-Za-z0-9-]{5,64}",self.account):raise ValueError("Invalid account")
        payload=self.transport("/v3/accounts/"+quote(self.account)+"/pricing?"+urlencode({"instruments":",".join(instruments)}))
        result={}
        for item in payload.get("prices",[]):
            symbol=item["instrument"]
            if symbol not in instruments:continue
            if not item.get("bids") or not item.get("asks"):raise ValueError("Missing executable bid/ask")
            result[symbol]={"bid":float(item["bids"][0]["price"]),"ask":float(item["asks"][0]["price"]),
                "timestamp":item["time"],"tradeable":item.get("status")=="tradeable"}
        if set(result)!=set(instruments):raise ValueError("Missing instrument quotes")
        return result

    def account_summary(self):
        if not re.fullmatch(r"[A-Za-z0-9-]{5,64}",self.account):raise ValueError("Invalid account")
        result=self.transport("/v3/accounts/"+quote(self.account)+"/summary")
        a=result["account"]
        return {"currency":a.get("currency"),"balance":a.get("balance"),"NAV":a.get("NAV"),"openTradeCount":a.get("openTradeCount")}
