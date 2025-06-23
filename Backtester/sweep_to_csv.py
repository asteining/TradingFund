# Backtester/sweep_to_csv.py
import json, pathlib, pandas as pd, numpy as np, os

root   = pathlib.Path(__file__).parents[1]
cfg    = json.load(open(root / "config.json"))
symbol = cfg["symbol"]

sweep_dir = root / "API" / "pnl_sweep" / symbol
rows = []

for f in sweep_dir.glob("pnl_*.json"):
    _, period, dev, stake = f.stem.split("_")
    pnl = pd.read_json(f)
    ret = pd.Series(pnl["value"]).pct_change().dropna()
    sharpe = np.sqrt(252) * ret.mean() / ret.std() if not ret.empty else np.nan
    dd = (pd.Series(pnl["value"]) / pd.Series(pnl["value"]).cummax() - 1).min()
    rows.append({
        "period": int(period),
        "devfactor": float(dev),
        "stake": int(stake),
        "total_return": pnl["value"].iloc[-1] / pnl["value"].iloc[0] - 1,
        "sharpe": sharpe,
        "max_drawdown": dd,
        "final_pnl": pnl["value"].iloc[-1]
    })

pd.DataFrame(rows).sort_values("sharpe", ascending=False) \
  .to_csv(root / "API" / f"sweep_summary_{symbol.lower()}.csv", index=False)

print("\u2713 sweep_summary written for", symbol)
