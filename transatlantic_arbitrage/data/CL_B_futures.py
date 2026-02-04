import pandas as pd
from tvDatafeed import TvDatafeed, Interval
import src.config as config

def fetch_arb_data():
    tv = TvDatafeed()
    
    df_brent = tv.get_hist(
        symbol=config.BRENT_TICKER,
        exchange=config.BRENT_EXCHANGE,
        interval=Interval.in_daily,
        n_bars=config.HISTORY_BARS
    )
    
    df_wti = tv.get_hist(
        symbol=config.WTI_TICKER,
        exchange=config.WTI_EXCHANGE,
        interval=Interval.in_daily,
        n_bars=config.HISTORY_BARS
    )
    
    if df_brent is None or df_wti is None:
        return None
    
    df_brent = df_brent.reset_index()
    df_wti = df_wti.reset_index()
    
    df_brent['datetime'] = pd.to_datetime(df_brent['datetime'])
    df_wti['datetime'] = pd.to_datetime(df_wti['datetime'])
    
    df_brent = df_brent.set_index('datetime')
    df_wti = df_wti.set_index('datetime')
    
    df_merged = pd.merge(
        df_brent[['close']].rename(columns={'close': 'Close_Brent'}),
        df_wti[['close']].rename(columns={'close': 'Close_WTI'}),
        left_index=True,
        right_index=True,
        how='inner'
    )
    
    return df_merged
