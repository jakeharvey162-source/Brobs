# SPDX-License-Identifier: GPL-3.0-only
"""Original BROBS adapter. Install Freqtrade separately; start with dry-run."""
from freqtrade.strategy import IStrategy
from brobs.freqtrade_bridge import columns,stake_cap

class BrobsStrategy(IStrategy):
    INTERFACE_VERSION=3
    timeframe='1h'
    can_short=False
    startup_candle_count=200
    process_only_new_candles=True
    stoploss=-.02
    minimal_roi={'0':.04}
    trailing_stop=False
    use_exit_signal=True
    exit_profit_only=False
    ignore_roi_if_entry_signal=False
    def populate_indicators(self,dataframe,metadata):return columns(dataframe)
    def populate_entry_trend(self,dataframe,metadata):
        dataframe['enter_long']=0
        dataframe.loc[dataframe['brobs_buy']&(dataframe['volume']>0),'enter_long']=1
        return dataframe
    def populate_exit_trend(self,dataframe,metadata):
        dataframe['exit_long']=0
        dataframe.loc[dataframe['brobs_sell']&(dataframe['volume']>0),'exit_long']=1
        return dataframe
    def custom_stake_amount(self,pair,current_time,current_rate,proposed_stake,min_stake,max_stake,leverage,entry_tag,side,**kwargs):
        if leverage!=1 or side!='long':return 0
        return stake_cap(self.wallets.get_total_stake_amount(),current_rate,proposed_stake,min_stake,max_stake)
