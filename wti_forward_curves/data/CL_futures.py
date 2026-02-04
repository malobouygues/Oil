import os
import pandas as pd
from datetime import datetime, timedelta
from tvDatafeed import TvDatafeed, Interval

def download_oil_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, 'df_oil.csv')
    
    # Vider le fichier existant avant de télécharger de nouvelles données
    if os.path.exists(output_path):
        os.remove(output_path)
        print("Fichier df_oil.csv vidé avant téléchargement")
    
    month_codes = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
    
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    contracts = []
    for i in range(12):
        month_idx = (current_month + i) % 12
        year_offset = (current_month + i) // 12
        contract_year = current_year + year_offset
        month_code = month_codes[month_idx]
        ticker = f"CL{month_code}{contract_year}"
        contracts.append(ticker)
    
    tv = TvDatafeed()
    df_oil = None
    
    n_bars = 110
    
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
                print(f"{ticker}: {len(df_close)} lignes téléchargées")
    
    if df_oil is not None and not df_oil.empty:
        df_oil = df_oil.sort_index()
        df_oil = df_oil[~df_oil.index.duplicated(keep='last')]
        df_oil.to_csv(output_path)
        print(f"\nSauvegarde effectuée: {len(df_oil)} lignes et {len(df_oil.columns)} colonnes dans df_oil.csv")
        return True
    else:
        print("Aucune donnée récupérée")
        return False

if __name__ == "__main__":
    download_oil_data()
