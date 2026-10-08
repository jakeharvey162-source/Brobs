"""Optional Backtrader baseline; uses its actual next-bar order execution engine.

This SMA baseline has no brackets/news filter. It is not a performance claim
about the Backtrader project or a cost-identical comparison with BROBS.
"""
import argparse
import json
import tempfile
from pathlib import Path
from .fx_research import load_forex_csv

def evaluate(rows,holdout=.3):
    import backtrader as bt
    from statistics import mean
    start=int(len(rows)*(1-holdout));warmup=max(0,start-30)
    class Strategy(bt.Strategy):
        def __init__(self):self.pending=None
        def notify_order(self,order):
            if order.status in (order.Completed,order.Canceled,order.Margin,order.Rejected):self.pending=None
        def next(self):
            if len(self.data)<=start-warmup or self.pending:return
            closes=[self.data.close[-j] for j in reversed(range(min(30,len(self.data))))]
            direction=1 if mean(closes[-8:])>mean(closes[-21:]) else -1
            if self.position and self.position.size*direction<0:self.pending=self.close()
            elif not self.position:
                units=int(self.broker.getvalue()*.2/self.data.close[0])
                if units:self.pending=self.buy(size=units) if direction>0 else self.sell(size=units)
    class USDNotional(bt.CommInfoBase):
        params=(('stocklike',False),('commtype',bt.CommInfoBase.COMM_PERC),('percabs',True),('commission',0.0),('automargin',1.0),('mult',1.0))
    with tempfile.TemporaryDirectory() as folder:
        path=Path(folder)/'bars.csv'
        with path.open('w') as f:
            f.write('datetime,open,high,low,close,volume\n')
            for r in rows[warmup:]:f.write(r['timestamp'].strftime('%Y-%m-%d %H:%M:%S')+','+','.join(str(r[k]) for k in ('open','high','low','close','volume'))+'\n')
        cerebro=bt.Cerebro();cerebro.addstrategy(Strategy)
        cerebro.adddata(bt.feeds.GenericCSVData(dataname=str(path),dtformat='%Y-%m-%d %H:%M:%S',timeframe=bt.TimeFrame.Minutes,compression=60,openinterest=-1))
        cerebro.broker.setcash(10000);cerebro.broker.addcommissioninfo(USDNotional())
        # Fraction approximates half the assumed EURUSD spread plus slippage.
        cerebro.broker.set_slippage_perc(.00012,slip_open=True)
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer,_name='trades');cerebro.addanalyzer(bt.analyzers.DrawDown,_name='drawdown')
        strategy=cerebro.run()[0];trades=strategy.analyzers.trades.get_analysis()
        closed=trades.get('total',{}).get('closed',0);wins=trades.get('won',{}).get('total',0);losses=trades.get('lost',{}).get('total',0)
        return dict(engine='backtrader 1.9.78.123',strategy='8/21 SMA regime baseline; no brackets',
            return_pct=round((cerebro.broker.getvalue()/10000-1)*100,4),max_drawdown_pct=round(strategy.analyzers.drawdown.get_analysis()['max']['drawdown'],4),
            closed_trades=closed,wins=wins,losses=losses,win_rate_pct=round(wins/closed*100,2) if closed else None,
            note='Independent engine baseline. Different stop and spread assumptions; not an apples-to-apples superiority test. Open trades remain marked.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);a=p.parse_args();print(json.dumps(evaluate(load_forex_csv(a.csv)),indent=2))
if __name__=='__main__':main()
