import requests
import pandas as pd
from loguru import logger

BASE_URL = "https://api-sntj.grakzjc49jfnj.ap-southeast-2.cs.amazonlightsail.com"

symbols = ['AAPL', 'V', 'ABNB', 'CRM', 'TSLA']
variables = {}
df_all = []
for symbol in symbols:
    ohlc_endpoint = f"{BASE_URL}/v0/ohlc/{symbol}"
    params = {"skip": 0, "limit": 300}

    response = requests.get(ohlc_endpoint, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes
    logger.info(f"Response status code for {symbol}: {response.status_code}")
    variables[f'df_{symbol}'] = pd.DataFrame(response.json())

    df_all.append(variables[f'df_{symbol}'] )

df_all = pd.concat(df_all, ignore_index=True)

#transformation
df_all.rename(columns={
    'timestamp_ms': 'date',
    'adj_high': 'high',
    'adj_low': 'low',
    'adj_close': 'close',
    'adj_open': 'open',
    'symbol_id': 'symbol'
}, inplace=True)

#datetime
df_all['date'] = pd.to_datetime(df_all['date'], unit='ms').dt.normalize()

columns_to_keep = ['symbol', 'date','volume', 'high', 'close', 'low', 'open']
df_all = df_all[columns_to_keep]

df_all.to_csv('data/stock_data.csv', index=False)
logger.info("Data saved to data/stock_data.csv")