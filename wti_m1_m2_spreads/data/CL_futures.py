import os
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tvDatafeed import TvDatafeed, Interval

# Month codes mapping: F=Jan, G=Feb, H=Mar, J=Apr, K=May, M=Jun, N=Jul, Q=Aug, U=Sep, V=Oct, X=Nov, Z=Dec
MONTH_CODES = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']

def get_contract_date(year, month_code):
    """Convert year and month code to actual contract date (first day of expiration month)."""
    month_idx = MONTH_CODES.index(month_code)
    # Month codes are 0-indexed: F=0 (Jan), G=1 (Feb), ..., Z=11 (Dec)
    return datetime(year, month_idx + 1, 1)

def download_cl_futures():
    """Download WTI Crude Oil futures data starting from CLN2020 (July 2020) to current M2 contract."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Script is already in data/ directory, so save CSV files here
    os.makedirs(script_dir, exist_ok=True)
    
    tv = TvDatafeed()
    now = datetime.now()
    stop_date = now + relativedelta(months=2)  # M2 contract (current date + 2 months)
    
    # Start from CLN2020 (July 2020, month code N)
    start_year = 2020
    start_month_code = 'N'  # July 2020
    
    year = start_year
    month_idx = MONTH_CODES.index(start_month_code)
    
    while True:
        month_code = MONTH_CODES[month_idx]
        ticker = f"CL{month_code}{year}"
        
        # Check if contract date is more than 2 months into the future
        contract_date = get_contract_date(year, month_code)
        if contract_date > stop_date:
            break
        
        filename = f"{ticker}.csv"
        filepath = os.path.join(script_dir, filename)
        
        try:
            df = tv.get_hist(
                symbol=ticker,
                exchange="NYMEX",
                interval=Interval.in_daily,
                n_bars=55
            )
            
            if df is not None and not df.empty:
                df = df.reset_index()
                df['datetime'] = pd.to_datetime(df['datetime']).dt.date
                df = df[['datetime', 'close', 'volume']]
                df.to_csv(filepath, index=False, header=False)
                print(f"{ticker}: {len(df)} rows saved to {filename}")
            else:
                print(f"{ticker}: No data available")
                
        except Exception as e:
            print(f"{ticker}: Error - {str(e)}")
        
        # Move to next month
        month_idx += 1
        if month_idx >= 12:
            month_idx = 0
            year += 1

if __name__ == "__main__":
    download_cl_futures()
