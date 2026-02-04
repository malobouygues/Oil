import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from src.spreads import calculate_volume_rolling_spread

df_result = calculate_volume_rolling_spread()

if df_result is None or len(df_result) == 0:
    print("No data available")
else:
    if 'spread' not in df_result.columns:
        print("Spread calculation failed")
    else:
        plt.figure(figsize=(12, 6))
        
        plt.plot(df_result.index, df_result['spread'], 
                 label='Volume-Based Rolling Spread', color='orange', linewidth=2)
        
        if 'z_score' in df_result.columns:
            z_above_2 = df_result['z_score'] > 2
            z_below_minus_2 = df_result['z_score'] < -2
            
            if z_above_2.any():
                plt.scatter(df_result.index[z_above_2], df_result['spread'][z_above_2], 
                           color='red', marker='o', s=30, label='Z-Score > 2', zorder=5)
            
            if z_below_minus_2.any():
                plt.scatter(df_result.index[z_below_minus_2], df_result['spread'][z_below_minus_2], 
                           color='blue', marker='o', s=30, label='Z-Score < -2', zorder=5)
        
        if 'rolling_mean' in df_result.columns:
            plt.plot(df_result.index, df_result['rolling_mean'], 
                    color='gray', linestyle='-', linewidth=1, label='Rolling Mean (252d)', alpha=0.7)
        
        plt.axhline(y=0, color='black', linestyle='--', linewidth=0.5, alpha=0.3)
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
        plt.xticks(rotation=0)
        plt.legend()
        plt.title('WTI Crude Oil Volume-Based Rolling Spread (M1 - M2)', 
                 fontsize=12, fontweight='bold')
        plt.xlabel('Date', fontsize=10)
        plt.ylabel('Spread ($)', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
