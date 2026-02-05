import os
import pandas as pd
from datetime import datetime, timedelta
from tvDatafeed import TvDatafeed, Interval

MONTH_CODES = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']

def get_contract_date(year, month_code):
    month_idx = MONTH_CODES.index(month_code)
    return datetime(year, month_idx + 1, 1)

def download_cl_futures():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(script_dir, exist_ok=True)
    
    tv = TvDatafeed()
    now = datetime.now()
    
    year_offset = 0
    month_offset = 2
    if now.month + month_offset > 12:
        year_offset = 1
        month_offset = month_offset - 12
    stop_date = datetime(now.year + year_offset, now.month + month_offset, 1)
    
    start_year = 2020
    start_month_code = 'N'
    
    year = start_year
    month_idx = MONTH_CODES.index(start_month_code)
    
    while True:
        month_code = MONTH_CODES[month_idx]
        ticker = f"CL{month_code}{year}"
        
        contract_date = get_contract_date(year, month_code)
        if contract_date > stop_date:
            break
        
        filename = f"{ticker}.csv"
        filepath = os.path.join(script_dir, filename)
        
        df = None
        try:
            df = tv.get_hist(
                symbol=ticker,
                exchange="NYMEX",
                interval=Interval.in_daily,
                n_bars=55
            )
        except Exception as e:
            df = None
        
        if df is not None and not df.empty:
            df = df.reset_index()
            df['datetime'] = pd.to_datetime(df['datetime']).dt.date
            df = df[['datetime', 'close', 'volume']]
            df.to_csv(filepath, index=False, header=False)
            print(f"{filename}: {len(df)} rows saved (ticker: {ticker})")
        else:
            print(f"{filename}: No data available (ticker: {ticker})")
        
        month_idx += 1
        if month_idx >= 12:
            month_idx = 0
            year += 1

if __name__ == "__main__":
    download_cl_futures()
