import pandas as pd
import numpy as np
import os
from datetime import datetime
import glob

MONTH_CODE_TO_NUM = {'F': 1, 'G': 2, 'H': 3, 'J': 4, 'K': 5, 'M': 6, 
                     'N': 7, 'Q': 8, 'U': 9, 'V': 10, 'X': 11, 'Z': 12}

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(script_dir, 'data')
start_date = pd.to_datetime('2020-06-01')

def parse_contract_filename(filename):
    basename = os.path.basename(filename)
    if not basename.startswith('CL') or not basename.endswith('.csv'):
        return None
    contract_code = basename[2:-4]
    if len(contract_code) < 5:
        return None
    month_code = contract_code[0]
    year_str = contract_code[1:]
    if month_code not in MONTH_CODE_TO_NUM:
        return None
    year = int(year_str)
    month = MONTH_CODE_TO_NUM[month_code]
    expiration_date = pd.to_datetime(f'{year}-{month:02d}-01')
    return {'filename': filename, 'ticker': basename[:-4], 'expiration': expiration_date, 
            'year': year, 'month': month, 'month_code': month_code}

def load_contract_data(filepath):
    df = pd.read_csv(filepath, header=None, names=['date', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] >= start_date].copy()
    return df

def calculate_volume_rolling_spread():
    csv_files = glob.glob(os.path.join(data_dir, 'CL*.csv'))
    contracts_info = []
    
    for filepath in csv_files:
        parsed = parse_contract_filename(filepath)
        if parsed:
            contracts_info.append(parsed)
    
    contracts_info.sort(key=lambda x: x['expiration'])
    
    if len(contracts_info) < 2:
        return None
    
    last_two_contracts = contracts_info[-2:]
    
    contracts_data = {}
    for contract in last_two_contracts:
        df = load_contract_data(contract['filename'])
        if not df.empty:
            contracts_data[contract['ticker']] = df.set_index('date')
    
    if len(contracts_data) < 2:
        return None
    
    contract_tickers = [c['ticker'] for c in last_two_contracts if c['ticker'] in contracts_data]
    
    if len(contract_tickers) < 2:
        return None
    
    m1_ticker = contract_tickers[0]
    m2_ticker = contract_tickers[1]
    
    df_m1 = contracts_data[m1_ticker]
    df_m2 = contracts_data[m2_ticker]
    
    min_date = max(df_m1.index.min(), df_m2.index.min())
    max_date = min(df_m1.index.max(), df_m2.index.max(), pd.to_datetime(datetime.now()))
    
    date_range = pd.date_range(start=min_date, end=max_date, freq='D')
    df_result = pd.DataFrame(index=date_range)
    df_result['spread'] = np.nan
    df_result['active_m1'] = m1_ticker
    df_result['active_m2'] = m2_ticker
    
    for date in date_range:
        if date not in df_m1.index or date not in df_m2.index:
            continue
        
        close_m1 = df_m1.loc[date, 'close']
        close_m2 = df_m2.loc[date, 'close']
        
        if pd.notna(close_m1) and pd.notna(close_m2):
            spread = close_m1 - close_m2
            df_result.loc[date, 'spread'] = spread
    
    df_result = df_result.dropna(subset=['spread'])
    
    if df_result.empty:
        return None
    
    rolling_window = 252
    df_result['rolling_mean'] = df_result['spread'].rolling(window=rolling_window, min_periods=1).mean()
    df_result['rolling_std'] = df_result['spread'].rolling(window=rolling_window, min_periods=1).std()
    df_result['z_score'] = (df_result['spread'] - df_result['rolling_mean']) / df_result['rolling_std'].replace(0, np.nan)
    df_result['z_score'] = df_result['z_score'].fillna(0)
    
    return df_result
