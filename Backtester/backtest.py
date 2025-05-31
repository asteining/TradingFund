# Backtester/backtest.py

import os
import argparse
import pandas as pd
import json

import backtrader as bt

from sqlalchemy import MetaData, Table, select
from db import engine
from strategies.mean_reversion import MeanReversionStrategy


def fetch_data_from_db(symbol: str) -> pd.DataFrame:
    """
    Query the SQLite table for `symbol` and return a DataFrame with
    index=Date and columns: [Open, High, Low, Close, Adj Close, Volume].
    Uses SQLAlchemy reflection (MetaData + Table) under SQLAlchemy 1.4+.
    """
    symbol = symbol.upper()

    # Reflect the table structure for this symbol
    metadata = MetaData()  # no bind=engine
    table = Table(symbol, metadata, autoload_with=engine)

    # Build a SELECT * FROM <symbol> statement
    stmt = select(table)

    # Let pandas load the result into a DataFrame, with Date as the index
    df = pd.read_sql(stmt, con=engine, index_col="Date", parse_dates=["Date"])
    return df


def run_backtest(symbol: str, start: str, end: str, initial_cash: float, output_json: str):
    """
    1) Pull price data from SQLite via fetch_data_from_db()
    2) Run Backtrader simulation with MeanReversionStrategy
    3) Write out a daily P&L series to a JSON file (output_json)
    """
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(initial_cash)

    # Fetch data from the database
    df = fetch_data_from_db(symbol)

    # Filter by date range
    df = df.loc[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]

    # Convert the Pandas DataFrame into a Backtrader data feed
    data_feed = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(MeanReversionStrategy)

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():,.2f}")
    results = cerebro.run()
    print(f"Final Portfolio Value:   {cerebro.broker.getvalue():,.2f}")

    # ---------------------------------------------------------------
    # ### UPDATED SECTION ###
    # Instead of using strat.broker._valuehist, use strat.value_history:
    strat = results[0]  # our lone instance of MeanReversionStrategy
    value_history = strat.value_history  # list of floats (one entry per bar)
    dates = df.index.tolist()            # list of pandas.Timestamp

    # Zip them into a list of dicts: [{ "date": "YYYY-MM-DD", "value": float }, ...]
    pnl_data = []
    for dt, port_val in zip(dates, value_history):
        pnl_data.append({"date": dt.strftime("%Y-%m-%d"), "value": port_val})

    # Write the P&L series to the specified JSON file
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w") as f:
        json.dump(pnl_data, f, indent=2)

    print(f"P&L series written to {output_json}")
    # ### END OF UPDATED SECTION ###
    # ---------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a backtest for a given symbol.")
    parser.add_argument(
        "--symbol", type=str, required=True, help="Ticker symbol (must match a table in market_data.db)."
    )
    parser.add_argument(
        "--start", type=str, required=True, help="Start date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--end", type=str, required=True, help="End date (YYYY-MM-DD)."
    )
    parser.add_argument(
        "--cash", type=float, default=100_000, help="Initial capital (USD)."
    )
    parser.add_argument(
        "--output", type=str, default="pnl.json", help="Path to write P&L JSON."
    )
    args = parser.parse_args()

    run_backtest(
        symbol=args.symbol.upper(),
        start=args.start,
        end=args.end,
        initial_cash=args.cash,
        output_json=args.output,
    )
