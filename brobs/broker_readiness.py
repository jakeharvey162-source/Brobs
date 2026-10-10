"""Read-only OANDA account and broker-journal readiness audit.

Works with practice or live account tokens. The live mode makes *GET requests
only* and never places, closes or modifies any order. This module is NOT an
activation path for unattended real-money trading.
"""
import argparse
import json
import os
import re
import sqlite3
from urllib.request import Request, build_opener, HTTPRedirectHandler

BASES = {
    "practice": "https://api-fxpractice.oanda.com",
    "live": "https://api-fxtrade.oanda.com",
}
class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError("Unexpected broker redirect")

def _account_valid(account):
    return isinstance(account,str) and bool(re.fullmatch(r"[A-Za-z0-9-]{5,64}",account))

class OandaReadiness:
    def __init__(self,environment="practice",token=None,account=None,transport=None):
        if environment not in BASES:
            raise ValueError("Only OANDA practice/live audit environments are recognized")
        prefix="OANDA_PRACTICE_" if environment=="practice" else "OANDA_LIVE_"
        self.environment=environment
        self.token=token if token is not None else os.getenv(prefix+"TOKEN","")
        self.account=account if account is not None else os.getenv(prefix+"ACCOUNT","")
        if not self.token or not _account_valid(self.account):
            raise ValueError("Missing environment-specific OANDA credentials")
        self.transport=transport or self._read
    def _read(self,path):
        if not path.startswith("/v3/accounts/"+self.account+"/"):
            raise ValueError("Read-only account path mismatch")
        req=Request(BASES[self.environment]+path,method="GET",headers={
            "Accept":"application/json","Authorization":"Bearer "+self.token,
        })
        with build_opener(_NoRedirect()).open(req,timeout=12) as response:
            raw=response.read(150001)
        if len(raw)>150000:raise ValueError("Oversized broker response")
        return json.loads(raw)
    def audit(self,journal=None):
        prefix="/v3/accounts/"+self.account
        account=self.transport(prefix+"/summary")["account"]
        reasons=[]
        if account.get("currency")!="USD":
            reasons.append("Currency is not USD; existing sizing has no cross-currency conversion")
        if account.get("mt4AccountID"):
            reasons.append("MT4-linked account is incompatible with BROBS client extensions")
        for field in ("NAV","balance"):
            try:
                from math import isfinite
                value=float(account[field])
                if not isfinite(value) or value<=0:reasons.append(field+" is not a positive finite value")
            except (ValueError,TypeError,KeyError):reasons.append(field+" missing or invalid")
        try:
            open_count=int(account["openTradeCount"])
            pending_count=int(account["pendingOrderCount"])
            if open_count<0 or pending_count<0:
                reasons.append("Invalid broker position/order counts")
        except (ValueError,TypeError,KeyError):
            reasons.append("Invalid broker position/order counts")
            open_count=pending_count=None
        trades=self.transport(prefix+"/openTrades")
        orders=self.transport(prefix+"/pendingOrders")
        if not isinstance(trades.get("trades"),list) or not isinstance(orders.get("orders"),list):
            reasons.append("Unable to inspect open trades/pending orders")
            trade_rows=order_rows=[]
        else:
            trade_rows=trades["trades"]
            order_rows=orders["orders"]
        if open_count is not None and open_count!=len(trade_rows):
            reasons.append("Broker open-trade count disagrees with openTrades response")
        if pending_count is not None and pending_count!=len(order_rows):
            reasons.append("Broker pending-order count disagrees with pendingOrders response")
        if trade_rows:
            reasons.append("Account contains open broker trades: automation must not take ownership")
        if order_rows:
            reasons.append("Account contains pending broker orders: automation must not take ownership")
        if journal:
            try:
                with sqlite3.connect("file:"+str(journal)+"?mode=ro",uri=True) as db:
                    binding=db.execute("SELECT account FROM broker_binding").fetchall()
                    uncertain=db.execute("SELECT COUNT(*) FROM broker_attempts WHERE status IN ('uncertain','filled_unverified_protection')").fetchone()[0]
                    if binding!=[(self.account,)]:
                        reasons.append("Broker journal belongs to another account")
                    if uncertain:
                        reasons.append(str(uncertain)+" unresolved order attempts require manual broker reconciliation")
            except (OSError,sqlite3.DatabaseError,ValueError):
                reasons.append("Broker journal cannot be read/verified")
        return {
            "environment":self.environment,
            "broker":"OANDA v20",
            "transport":"read-only GET",
            "connection_checked":True,
            "market_order_submission_enabled":False,
            "real_money_execution_enabled":False,
            "audit_passed":not reasons,
            "limitations":[
                "No automated broker order lifecycle/reconciliation in this version",
                "No independently verified profitable strategy or forward-paper track record",
                "No credentialed end-to-end execution test on the receiving broker",
                "Passing account checks alone never authorizes execution",
            ],
            "blockers":reasons,
        }

def main():
    parser=argparse.ArgumentParser(description="BROBS OANDA read-only account audit: never places an order")
    parser.add_argument("--environment",choices=("practice","live"),default="practice")
    parser.add_argument("--journal",help="Optional existing OANDA practice-order journal, read-only")
    args=parser.parse_args()
    try:
        report=OandaReadiness(args.environment).audit(args.journal)
    except Exception as exc:
        # Never print external exception bodies; upstream responses may contain secrets.
        print(json.dumps({"environment":args.environment,"audit_passed":False,"connection_checked":False,
                          "market_order_submission_enabled":False,"real_money_execution_enabled":False,
                          "error_type":type(exc).__name__}))
        raise SystemExit(2)
    print(json.dumps(report,indent=2))
    if not report["audit_passed"]:raise SystemExit(2)

if __name__=="__main__":
    main()
