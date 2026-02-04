import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import src.config as config
from src.data_loader import fetch_arb_data

plt.style.use('bmh')

df_prices = fetch_arb_data()

if df_prices is None or len(df_prices) == 0:
    print("No data available")
else:
    df_prices['Spread_Gross'] = df_prices['Close_Brent'] - df_prices['Close_WTI']
    df_prices['Arb_Incentive'] = df_prices['Spread_Gross'] - config.FREIGHT_COST
    df_prices['Arb_Open'] = df_prices['Arb_Incentive'] > 0
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    ax1.plot(df_prices.index, df_prices['Close_Brent'], 
             label='Brent (UKOIL)', color='red', linewidth=2)
    ax1.plot(df_prices.index, df_prices['Close_WTI'], 
             label='WTI (USOIL)', color='gray', linewidth=2)
    ax1.set_ylabel('Price (USD/bbl)', fontsize=10)
    ax1.set_title('Absolute Prices', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2.fill_between(df_prices.index, df_prices['Arb_Incentive'], 0,
                     where=(df_prices['Arb_Incentive'] > 0),
                     color='green', alpha=0.3, label='Arb Open')
    ax2.fill_between(df_prices.index, df_prices['Arb_Incentive'], 0,
                     where=(df_prices['Arb_Incentive'] <= 0),
                     color='red', alpha=0.3, label='Arb Closed')
    ax2.plot(df_prices.index, df_prices['Arb_Incentive'], 
             color='black', linewidth=2, label='Arb Incentive')
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=0.5, alpha=0.3)
    ax2.axhline(y=-config.FREIGHT_COST, color='blue', linestyle='--', 
                linewidth=1, alpha=0.5, label=f'Freight Cost ({config.FREIGHT_COST} USD/bbl)')
    ax2.set_xlabel('Date', fontsize=10)
    ax2.set_ylabel('Arb Incentive (USD/bbl)', fontsize=10)
    ax2.set_title('Transatlantic Arb Spread', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()
