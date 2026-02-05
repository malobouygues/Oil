import os
import pandas as pd
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

MONTH_CODES = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']

def find_front_month(tv, ticker_prefix, exchange, now):
    current_year = now.year
    current_month_idx = now.month - 1
    
    for offset in [1, 0, 2]:
        test_month_idx = current_month_idx + offset
        test_year = current_year
        
        while test_month_idx >= 12:
            test_month_idx -= 12
            test_year += 1
        
        month_code = MONTH_CODES[test_month_idx]
        test_ticker = f"{ticker_prefix}{month_code}{test_year}"
        
        df = tv.get_hist(
            symbol=test_ticker,
            exchange=exchange,
            interval=Interval.in_daily,
            n_bars=5
        )
        
        if df is not None and not df.empty:
            last_date = pd.to_datetime(df.index[-1])
            days_since_last_trade = (now - last_date).days
            
            if days_since_last_trade <= 10:
                print(f"  Front month for {ticker_prefix}: {month_code}{test_year} (last trade: {last_date.date()})")
                return test_month_idx, test_year
    
    next_month_idx = current_month_idx + 1
    next_year = current_year
    if next_month_idx >= 12:
        next_month_idx -= 12
        next_year += 1
    print(f"  Could not determine front month for {ticker_prefix}, defaulting to {MONTH_CODES[next_month_idx]}{next_year}")
    return next_month_idx, next_year

def download_oil_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'df_oil.csv')
    
    if os.path.exists(output_path):
        os.remove(output_path)
    
    tv = TvDatafeed()
    now = datetime.now()
    
    print(f"\nDetermining front month for CL...")
    front_month_idx, front_year = find_front_month(tv, 'CL', 'NYMEX', now)
    
    contracts = []
    current_month_idx = front_month_idx
    current_year = front_year
    
    for i in range(12):
        target_month_idx = current_month_idx + i
        target_year = current_year
        
        while target_month_idx >= 12:
            target_month_idx -= 12
            target_year += 1
        
        month_code = MONTH_CODES[target_month_idx]
        ticker = f"CL{month_code}{target_year}"
        contracts.append(ticker)
    
    df_oil = None
    
    n_bars = 25
    
    for ticker in contracts:
        df = tv.get_hist(
            symbol=ticker,
            exchange="NYMEX",
            interval=Interval.in_daily,
            n_bars=n_bars
        )
        
        if df is not None and not df.empty:
            df = df.reset_index()
            df['datetime'] = pd.to_datetime(df['datetime'])
            df = df.set_index('datetime')
            df_close = df[['close']].rename(columns={'close': ticker})
            
            if not df_close.empty:
                if df_oil is None:
                    df_oil = df_close
                else:
                    df_oil = df_oil.join(df_close, how='outer')
                print(f"{ticker}: {len(df_close)} rows downloaded")
    
    if df_oil is not None and not df_oil.empty:
        df_oil = df_oil.sort_index()
        df_oil = df_oil[~df_oil.index.duplicated(keep='last')]
        df_oil.to_csv(output_path, date_format='%Y-%m-%d')
        print(f"df_oil.csv: {len(df_oil)} rows and {len(df_oil.columns)} columns saved")
        return True
    else:
        print("df_oil.csv: No data available")
        return False

if __name__ == "__main__":
    download_oil_data()
