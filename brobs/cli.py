"""Usage: python -m brobs.cli --csv candles.csv --market crypto --symbol BTCUSD"""
import argparse,json
from .history import load_csv
from .backtest import backtest

def main():
    p=argparse.ArgumentParser(description="BROBS AI historical paper backtest")
    p.add_argument("--csv",required=True)
    p.add_argument("--market",choices=["crypto","forex","stock"],required=True)
    p.add_argument("--symbol",required=True)
    p.add_argument("--cash",type=float,default=10000)
    a=p.parse_args()
    if a.cash<=0: p.error("--cash must be positive")
    print(json.dumps(backtest(load_csv(a.csv),a.symbol,a.market,a.cash),indent=2))
if __name__=="__main__": main()
