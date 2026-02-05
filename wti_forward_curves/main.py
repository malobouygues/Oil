import pandas as pd
import matplotlib.pyplot as plt

from src.curves import load_oil_data, get_current_curve, calculate_roll_yield, get_previous_month_curve

month_codes = ['F', 'G', 'H', 'J', 'K', 'M', 'N', 'Q', 'U', 'V', 'X', 'Z']
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
month_code_to_name = dict(zip(month_codes, month_names))

def format_ticker_label(ticker):
    if len(ticker) < 6 or not ticker.startswith('CL'):
        return ticker
    month_code = ticker[2]
    year = ticker[3:]
    year_short = year[-2:]
    month_name = month_code_to_name.get(month_code, month_code)
    return f"{month_name}-{year_short}\n({month_code})"

def format_pair_label(pair_str):
    if '-' not in pair_str:
        return pair_str
    parts = pair_str.split('-')
    if len(parts) != 2:
        return pair_str
    ticker1, ticker2 = parts
    if len(ticker1) >= 6 and len(ticker2) >= 6:
        month_code1 = ticker1[2]
        year1 = ticker1[3:][-2:]
        month_code2 = ticker2[2]
        year2 = ticker2[3:][-2:]
        return f"{month_code1}{year1}-{month_code2}{year2}"
    return pair_str

df_oil = load_oil_data()
current_curve = get_current_curve(df_oil)
roll_yield = calculate_roll_yield(df_oil)

if df_oil is None or len(df_oil) == 0:
    pass
else:
    if current_curve is not None and len(current_curve) > 0:
        common_date = df_oil.index[-1]
        target_date = common_date - pd.DateOffset(months=1)
        previous_curve, previous_date = get_previous_month_curve(df_oil, target_date)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
        
        if previous_curve is not None and len(previous_curve) > 0:
            common_tickers = current_curve.index.intersection(previous_curve.index)
            if len(common_tickers) > 0:
                x_positions = current_curve.index.get_indexer(common_tickers)
                ax1.plot(x_positions, 
                        previous_curve[common_tickers].values,
                        linestyle='--', linewidth=2, color='gray', 
                        label=f'Previous Month ({previous_date.strftime("%Y-%m-%d")})')
        
        ax1.plot(current_curve.index, current_curve.values, 
                marker='o', color='red', linewidth=2, label='Current')
        ax1.set_title('WTI Forward Curve', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Price (in dollars)', fontsize=10)
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(range(len(current_curve)))
        ax1.set_xticklabels([format_ticker_label(ticker) for ticker in current_curve.index], rotation=0)
        ax1.tick_params(labelbottom=True)
        ax1.legend()
        
        if roll_yield is not None and len(roll_yield) > 0:
            ax2.bar(range(len(roll_yield)), roll_yield.values, color='blue')
            ax2.set_title('Roll Yield', fontsize=12, fontweight='bold')
            ax2.set_xticks(range(len(roll_yield)))
            ax2.set_xticklabels([format_pair_label(pair) for pair in roll_yield.index], rotation=0)
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: '{:.1%}'.format(y)))
            ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.show()
    else:
        pass
