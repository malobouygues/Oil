import os

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tickers
BRENT_TICKER = 'UKOIL'
BRENT_EXCHANGE = 'ICEEUR'
WTI_TICKER = 'USOIL'
WTI_EXCHANGE = 'NYMEX'

# Freight cost (USD/bbl)
FREIGHT_COST = 3.00

# History bars
HISTORY_BARS = 2000
