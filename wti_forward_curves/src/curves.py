import pandas as pd
import numpy as np
import os

def load_oil_data():
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(script_dir, 'data', 'df_oil.csv')
    df_oil = pd.read_csv(data_path, index_col=0, parse_dates=True)
    return df_oil

def get_current_curve(df_oil):
    available_cols = [col for col in df_oil.columns if df_oil[col].notna().any()]
    if len(available_cols) == 0:
        return None
    
    latest_row = df_oil[available_cols].iloc[-1]
    current_curve = latest_row.dropna()
    return current_curve

def calculate_roll_yield(df_oil):
    available_cols = [col for col in df_oil.columns if df_oil[col].notna().any()]
    if len(available_cols) < 2:
        return None
    
    latest_row = df_oil[available_cols].iloc[-1].dropna()
    if len(latest_row) < 2:
        return None
    
    price_front = latest_row.iloc[:-1].values
    price_next = latest_row.iloc[1:].values
    roll_yield = (price_front - price_next) / price_front
    
    tickers = [f"{latest_row.index[i]}-{latest_row.index[i+1]}" 
               for i in range(len(latest_row) - 1)]
    
    return pd.Series(roll_yield, index=tickers)
