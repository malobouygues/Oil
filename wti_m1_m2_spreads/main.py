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
                 label='Rolling Spread (based on volume)', color='orange', linewidth=2)
        
        if 'rolling_mean' in df_result.columns and 'rolling_std' in df_result.columns:
            upper_band = df_result['rolling_mean'] + 2 * df_result['rolling_std']
            lower_band = df_result['rolling_mean'] - 2 * df_result['rolling_std']
            
            plt.plot(df_result.index, upper_band, 
                    color='blue', linestyle='--', linewidth=1, alpha=0.5, label='±2 Std Dev', zorder=2)
            plt.plot(df_result.index, lower_band, 
                    color='blue', linestyle='--', linewidth=1, alpha=0.5, label='', zorder=2)
            
            plt.plot(df_result.index, df_result['rolling_mean'], 
                    color='gray', linestyle='-', linewidth=1.5, label='Rolling Mean (252d)', alpha=0.8, zorder=3)
        
        plt.axhline(y=0, color='black', linestyle='--', linewidth=0.5, alpha=0.3)
        
        plt.xlim(df_result.index.min(), df_result.index.max())
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        plt.xticks(rotation=0)
        
        y_min = df_result['spread'].min()
        y_max = df_result['spread'].max()
        y_ticks = np.arange(np.floor(y_min * 2) / 2, np.ceil(y_max * 2) / 2 + 0.5, 0.5)
        plt.yticks(y_ticks)
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1f}'))
        
        plt.legend()
        plt.title('WTI Oil Prompt Spread (M1 - M2)', 
                 fontsize=12, fontweight='bold')
        plt.xlabel('', fontsize=10)
        plt.ylabel('Spread', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()