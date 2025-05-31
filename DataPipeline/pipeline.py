import pandas as pd
from db import engine

def fetch_price(symbol, start, end):
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{symbol}?period1={start}&period2={end}&interval=1d'
    df = pd.read_csv(url)
    df.to_sql(symbol, engine, if_exists='replace')
    print(f'{symbol} data saved.')

if __name__ == '__main__':
    fetch_price('AAPL', '1609459200', '1711920000')  # Jan 1, 2021 to Apr 1, 2024
