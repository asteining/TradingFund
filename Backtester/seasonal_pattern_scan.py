# Backtester/seasonal_pattern_scan.py
import json, pathlib, pandas as pd, os
from sqlalchemy import text
from db import engine

root   = pathlib.Path(__file__).parents[1]
cfg    = json.load(open(root / "config.json"))
symbol = cfg["symbol"]

df = pd.read_sql(text(f'SELECT "Date","Close" FROM "{symbol}"'),
                 con=engine, parse_dates=["Date"]).set_index("Date")
daily = df["Close"].pct_change()

stats = (daily.groupby(daily.index.weekday)
              .agg(avg_return="mean",
                   t_stat=lambda x: x.mean()/x.std()*len(x)**0.5)
              .reset_index(names="weekday"))

out = root / "API" / f"seasonal_stats_{symbol.lower()}.json"
stats.to_json(out, orient="records", indent=2)
print("\u2713 seasonal stats written for", symbol)
