import os
import json
import pandas as pd
import numpy as np
import backtrader as bt
from sqlalchemy import MetaData, Table, select

from db import engine
from strategies.mean_reversion import MeanReversionStrategy


def load_table(name: str) -> pd.DataFrame:
    metadata = MetaData()
    table = Table(name, metadata, autoload_with=engine)
    stmt = select(table)
    df = pd.read_sql(stmt, con=engine, index_col="Date", parse_dates=["Date"])
    return df





def main():
    btc_df = load_table("CRYPTO_BTCUSD")
    eth_df = load_table("CRYPTO_ETHUSD")

    merged = btc_df[["Close"]].rename(columns={"Close": "BTC_Close"}).join(
        eth_df[["Close"]].rename(columns={"Close": "ETH_Close"}),
        how="inner",
    )

    spread_df = pd.DataFrame({
        "Date": merged.index,
        "Spread": merged["BTC_Close"] - merged["ETH_Close"],
    }).set_index("Date")

    # Backtrader's PandasData expects OHLC columns. Duplicate the spread
    # value across Open/High/Low/Close and supply a dummy Volume column.
    bt_df = pd.DataFrame(index=spread_df.index)
    bt_df["Open"] = spread_df["Spread"]
    bt_df["High"] = spread_df["Spread"]
    bt_df["Low"] = spread_df["Spread"]
    bt_df["Close"] = spread_df["Spread"]
    bt_df["Volume"] = 0

    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000.0)

    data_feed = bt.feeds.PandasData(dataname=bt_df)
    cerebro.adddata(data_feed)
    cerebro.addstrategy(MeanReversionStrategy, period=20, devfactor=2.0, stake=1)

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():,.2f}")
    results = cerebro.run()
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():,.2f}")

    strat = results[0]
    value_history = strat.value_history
    dates = bt_df.index.tolist()

    pnl_data = [
        {"date": dt.strftime("%Y-%m-%d"), "value": val}
        for dt, val in zip(dates, value_history)
    ]

    output_path = os.path.join(os.path.dirname(__file__), "..", "API", "pnl_spread_btc_eth.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(pnl_data, f, indent=2)
    print(f"P&L series written to {output_path}")

    # ---- Performance metrics ----
    returns = pd.Series(value_history).pct_change().dropna()
    if not returns.empty:
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252)
        running_max = pd.Series(value_history).cummax()
        drawdown = (pd.Series(value_history) - running_max) / running_max
        max_drawdown = drawdown.min()
    else:
        sharpe = 0.0
        max_drawdown = 0.0

    metrics = {
        "sharpe_ratio": float(sharpe),
        "max_drawdown": float(max_drawdown),
    }

    metrics_path = os.path.join(os.path.dirname(__file__), "..", "API", "metrics_spread.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print("Wrote ../API/metrics_spread.json")


if __name__ == "__main__":
    main()
