"""Real Freqtrade backtest with explicit synthetic market constraints, no exchange I/O."""
import argparse,json,tempfile,zipfile,hashlib
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from freqtrade.exchange import Exchange
from freqtrade.main import main

def offline_markets(self,*args,**kwargs):
    markets=[]
    for base in ('BTC','ETH'):
        markets.append(dict(id=base+'USDT',symbol=base+'/USDT',base=base,quote='USDT',baseId=base,quoteId='USDT',
            type='spot',spot=True,margin=False,swap=False,future=False,option=False,contract=False,active=True,
            linear=None,inverse=None,settle=None,settleId=None,contractSize=None,
            precision=dict(amount=.000001,price=.01),maker=.001,taker=.001,
            limits=dict(amount=dict(min=.000001,max=None),price=dict(min=.01,max=None),cost=dict(min=5,max=None)),info={}))
    self._api.set_markets(markets);self._api_async.set_markets(markets);self._markets=self._api.markets

def run(btc,eth,capital,output,fee=.001):
    root=Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory() as temp:
        user=Path(temp);data=user/'data'/'binance';data.mkdir(parents=True)
        for pair,source in [('BTC_USDT',btc),('ETH_USDT',eth)]:
            frame=pd.read_csv(source).rename(columns={'timestamp':'date'});frame['date']=pd.to_datetime(frame['date'],utc=True)
            frame.to_feather(data/(pair+'-1h.feather'))
        config=json.loads((root/'integrations/freqtrade/dry-run.json').read_text());config['dry_run_wallet']=capital
        config['exchange']['enable_ws']=False
        configfile=user/'config.json';configfile.write_text(json.dumps(config))
        # Backtesting only; patch market discovery, and refuse any unexpected network.
        with patch.object(Exchange,'reload_markets',offline_markets),patch('socket.socket.connect',side_effect=RuntimeError('Offline check: network refused')):
            try:main(['backtesting','--config',str(configfile),'--strategy','BrobsStrategy','--strategy-path',str(root/'integrations/freqtrade'),
                '--userdir',str(user),'--datadir',str(data),'--timerange','20260323-20261001','--fee',str(fee),'--cache','none','--export','trades'])
            except SystemExit as exc:
                if exc.code not in (None,0):raise
        files=list((user/'backtest_results').glob('*.zip'))
        if not files:raise RuntimeError('No engine result produced; do not report a passed backtest')
        with zipfile.ZipFile(files[-1]) as archive:
            names=[n for n in archive.namelist() if n.endswith('.json') and not n.endswith('.meta.json') and '_config' not in n]
            payload=json.loads(archive.read(names[0]))
        raw=payload['strategy']['BrobsStrategy']
        fields=['total_trades','wins','draws','losses','winrate','profit_total','profit_total_abs','profit_factor','max_drawdown_account','starting_balance','final_balance','backtest_start','backtest_end']
        result={k:raw[k] for k in fields}
        result['trades']=[{k:t.get(k) for k in ('pair','open_date','close_date','stake_amount','profit_abs','profit_ratio','exit_reason')} for t in raw['trades']]
        result['brobs_assumptions']=dict(engine='Freqtrade 2026.9',capital=capital,fee_per_fill=fee,
            metadata='Synthetic spot constraints: 5 USDT minimum cost, 0.000001 unit step, 0.01 price tick; not verified current Binance rules',
            live_exchange_tested=False,hypergrok_runtime_tested=False,future_win_probability=None,
            limitations='Reused historical periods; no explicit spread/slippage or order-book impact/live latency; equity is one shared BTC/ETH portfolio; no BROBS daily-loss/cooldown/Grok/news gates in this adapter; does not establish future accuracy',
            input_sha256={str(Path(p).name):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in (btc,eth)})
        Path(output).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--btc',required=True);p.add_argument('--eth',required=True)
    p.add_argument('--capital',type=float,default=10000);p.add_argument('--fee',type=float,default=.001)
    p.add_argument('--output',required=True);a=p.parse_args()
    run(a.btc,a.eth,a.capital,a.output,a.fee)
