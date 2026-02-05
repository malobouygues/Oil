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
    
    contracts_data = {}
    for contract in contracts_info:
        df = load_contract_data(contract['filename'])
        if not df.empty:
            contracts_data[contract['ticker']] = df.set_index('date')
    
    if len(contracts_data) < 2:
        return None
    
    all_dates = set()
    for df in contracts_data.values():
        all_dates.update(df.index)
    
    date_range = pd.date_range(start=start_date, end=pd.to_datetime(datetime.now()), freq='D')
    date_range = date_range[date_range.isin(all_dates)]
    
    if len(date_range) == 0:
        return None
    
    first_two_contracts = contracts_info[:2]
    current_m1_ticker = first_two_contracts[0]['ticker']
    current_m2_ticker = first_two_contracts[1]['ticker']
    
    if current_m1_ticker not in contracts_data or current_m2_ticker not in contracts_data:
        return None
    
    ticker_to_index = {c['ticker']: i for i, c in enumerate(contracts_info)}
    
    df_result = pd.DataFrame(index=date_range)
    df_result['spread'] = np.nan
    df_result['active_m1'] = ''
    df_result['active_m2'] = ''
    
    for date in date_range:
        if (current_m1_ticker not in contracts_data or 
            current_m2_ticker not in contracts_data or
            date not in contracts_data[current_m1_ticker].index or
            date not in contracts_data[current_m2_ticker].index):
            continue
        
        df_m1 = contracts_data[current_m1_ticker]
        df_m2 = contracts_data[current_m2_ticker]
        
        volume_m1 = df_m1.loc[date, 'volume']
        volume_m2 = df_m2.loc[date, 'volume']
        close_m1 = df_m1.loc[date, 'close']
        close_m2 = df_m2.loc[date, 'close']
        
        if pd.isna(volume_m1) or pd.isna(volume_m2) or pd.isna(close_m1) or pd.isna(close_m2):
            continue
        
        day_of_month = date.day
        should_roll = (volume_m2 > volume_m1) and (day_of_month >= 13)
        
        if should_roll:
            current_m2_idx = ticker_to_index.get(current_m2_ticker)
            
            if current_m2_idx is not None:
                next_m1_idx = current_m2_idx + 1
                
                if next_m1_idx < len(contracts_info):
                    next_m1_ticker = contracts_info[next_m1_idx]['ticker']
                    if (next_m1_ticker in contracts_data and 
                        date in contracts_data[next_m1_ticker].index):
                        current_m1_ticker = current_m2_ticker
                        current_m2_ticker = next_m1_ticker
                        df_m1 = contracts_data[current_m1_ticker]
                        df_m2 = contracts_data[current_m2_ticker]
                        close_m1 = df_m1.loc[date, 'close']
                        close_m2 = df_m2.loc[date, 'close']
        
        spread = close_m1 - close_m2
        df_result.loc[date, 'spread'] = spread
        df_result.loc[date, 'active_m1'] = current_m1_ticker
        df_result.loc[date, 'active_m2'] = current_m2_ticker
    
    df_result = df_result.dropna(subset=['spread'])
    
    if df_result.empty:
        return None
    
    rolling_window = 252
    df_result['rolling_mean'] = df_result['spread'].rolling(window=rolling_window, min_periods=1).mean()
    df_result['rolling_std'] = df_result['spread'].rolling(window=rolling_window, min_periods=1).std()
    df_result['z_score'] = (df_result['spread'] - df_result['rolling_mean']) / df_result['rolling_std'].replace(0, np.nan)
    df_result['z_score'] = df_result['z_score'].fillna(0)
    
    return df_result
