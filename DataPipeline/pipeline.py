# DataPipeline/pipeline.py

import time
import os
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
import argparse

import yfinance as yf  # yfinance handles rate‐limiting/retries
from db import engine   # SQLAlchemy engine from DataPipeline/db.py
from dotenv import load_dotenv
from crypto import fetch_crypto

# Load environment variables (DB_PATH, etc.) from DataPipeline/.env

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments for start and end dates."""
    parser = argparse.ArgumentParser(description="Ingest market data")
    parser.add_argument("--start", type=str, help="start date YYYY-MM-DD")
    parser.add_argument("--end", type=str, help="end date YYYY-MM-DD")
    return parser.parse_args()


def fetch_price_yahoo(symbol: str, period: str = "max") -> pd.DataFrame:
    """
    Download OHLCV for `symbol` using yfinance.
    - period: string like "1y", "2y", "max", etc.
    Returns a DataFrame with a timezone-aware Date index (we strip tz later),
    and columns: ["Open","High","Low","Close","Volume","Dividends","Stock Splits","Adj Close"].
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval="1d", auto_adjust=False)

    # Ensure the index is named "Date"
    df.index.name = "Date"

    # Keep only the columns we care about; yfinance sometimes returns extras
    df = df[["Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits", "Adj Close"]].copy()
    return df


def save_to_db(symbol: str, df: pd.DataFrame, start_date: datetime, end_date: datetime):
    """
    Write DataFrame to a SQL table named after the symbol (overwrite if exists).
    We strip the tz from the index before filtering by start/end dates.
    """
    # 1) Remove timezone information so comparisons to naive datetimes work
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)

    # 2) Filter by the requested date range
    mask = (df.index >= start_date) & (df.index <= end_date)
    df_filtered = df.loc[mask]

    # 3) Uppercase the table name
    table_name = symbol.upper()

    # 4) Write to SQLite via SQLAlchemy engine; index label = "Date"
    df_filtered.to_sql(name=table_name, con=engine, if_exists="replace", index_label="Date")
    print(f"Saved {len(df_filtered)} rows for {symbol} to table `{table_name}`.")


if __name__ == "__main__":
    args = parse_arguments()
    today = datetime.today()
    start_date = (
        datetime.strptime(args.start, "%Y-%m-%d")
        if args.start else today - timedelta(days=3650)
    )
    end_date = (
        datetime.strptime(args.end, "%Y-%m-%d") if args.end else today
    )

    print(f"Fetching data from {start_date.date()} through {end_date.date()}")

    # List of symbols you want to ingest
    symbols = ["AAPL", "MSFT", "GOOGL"]
    crypto_symbols = ["BTC/USDT"]

    for sym in symbols:
        print(f"Downloading {sym} …")
        try:
            # 1) Download the full history (“max”), then slice by date
            df = fetch_price_yahoo(sym, period="max")
            save_to_db(sym, df, start_date, end_date)
            time.sleep(2)  # polite pause between requests
        except Exception as e:
            print(f"❗ Error fetching {sym}: {e}")
            print("    Waiting 10 seconds and retrying once…")
            time.sleep(10)
            try:
                df = fetch_price_yahoo(sym, period="max")
                save_to_db(sym, df, start_date, end_date)
                time.sleep(2)
            except Exception as e2:
                print(f"❌ Second attempt failed for {sym}: {e2}")
                # Skip to next symbol without crashing
                continue

    for csym in crypto_symbols:
        print(f"Downloading crypto {csym} …")
        try:
            df = fetch_crypto(csym)
            table = f"CRYPTO_{csym.replace('/', '')}"
            save_to_db(table, df, start_date, end_date)
            time.sleep(2)
        except Exception as e:
            print(f"❗ Error fetching {csym}: {e}")
            continue

    print("Data ingestion complete.")
