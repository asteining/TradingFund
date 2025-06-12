import os
import json
import numpy as np
import pandas as pd
from sqlalchemy import MetaData, Table, select

# Reuse the SQLAlchemy engine from db.py in this folder
from db import engine


def load_data() -> pd.DataFrame:
    """Load BTC data from JSON or SQLite.

    Returns
    -------
    pd.DataFrame with index Date and column 'Close'.
    """
    json_path = os.path.join(os.path.dirname(__file__), "..", "API", "pnl_btc_mean_reversion.json")
    if os.path.isfile(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df.rename(columns={"value": "Close"}, inplace=True)
        df.set_index("date", inplace=True)
        df = df[["Close"]]
    else:
        metadata = MetaData()
        table = Table("CRYPTO_BTCUSD", metadata, autoload_with=engine)
        stmt = select(table.c.Date, table.c.Close)
        df = pd.read_sql(stmt, con=engine, parse_dates=["Date"])
        df.set_index("Date", inplace=True)
    return df


def main() -> None:
    df = load_data()
    df["returns"] = df["Close"].pct_change()
    df = df.dropna()
    df["weekday"] = df.index.day_name()

    grouped = df.groupby("weekday")["returns"]
    average_return = grouped.mean()
    sem = grouped.apply(lambda x: x.std(ddof=1) / np.sqrt(len(x)))
    t_stat = average_return / sem

    result = pd.DataFrame({
        "average_return": average_return,
        "standard_error": sem,
        "t_stat": t_stat,
    }).sort_values("t_stat", ascending=False)

    print(result.to_string(float_format=lambda x: f"{x: .6f}"))


if __name__ == "__main__":
    main()
