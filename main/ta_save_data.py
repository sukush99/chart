import requests
import pandas as pd
from loguru import logger

BASE_URL = "https://api-sntj.grakzjc49jfnj.ap-southeast-2.cs.amazonlightsail.com"

symbols = ['AAPL', 'V', 'ABNB', 'CRM', 'TSLA']
variables = {}
df_all_ta = []
for symbol in symbols:
    ohlc_endpoint = f"{BASE_URL}/v0/ohlc/{symbol}"
    params = {"skip": 0, "limit": 300}

    response = requests.get(ohlc_endpoint, params=params)
    response.raise_for_status()  # Raise an exception for bad status codes

    variables[f'df_{symbol}'] = pd.DataFrame(response.json())

    df_all_ta.append(variables[f'df_{symbol}'] )

df_all_ta = pd.concat(df_all_ta, ignore_index=True)

#transformation
df_all_ta.rename(columns={
    'timestamp_ms': 'date',
    'symbol_id': 'symbol'
}, inplace=True)

#datetime
df_all_ta['date'] = pd.to_datetime(df_all_ta['date'], unit='ms').dt.normalize()

columns_to_keep = ['symbol', 'date', 'ADJ_RSI_14', 'ADJ_MACD', 'ADJ_EMA_50', 'ADJ_SMA_50', 'ADJ_ATR_14', 'ADJ_OBV', 'ADJ_VWAP', 'ADJ_CCI_14']
df_all_ta = df_all_ta[columns_to_keep]

df_all_ta.to_csv('data/stock_data_ta.csv', index=False)
logger.info("Data saved to data/stock_data_ta.csv")