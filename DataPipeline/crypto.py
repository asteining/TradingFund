import time
from datetime import datetime
from typing import List

import ccxt
import pandas as pd


def fetch_crypto(symbol: str) -> pd.DataFrame:
    """Fetch daily OHLCV for a crypto symbol using ccxt (Binance)."""
    exchange = ccxt.binance()
    all_rows: List[List] = []
    since = None
    while True:
        data = exchange.fetch_ohlcv(symbol, timeframe="1d", since=since, limit=1000)
        if not data:
            break
        all_rows.extend(data)
        since = data[-1][0] + 24 * 60 * 60 * 1000
        if len(data) < 1000:
            break
        time.sleep(exchange.rateLimit / 1000)

    df = pd.DataFrame(all_rows, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["Date"], unit="ms")
    df.set_index("Date", inplace=True)
    return df
