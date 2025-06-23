# Backtester/parameter_sweep.py
"""
Grid-search wrapper that reads its settings from ../../config.json
and writes PnL files to API/pnl_sweep/<symbol>/.
"""

import json, pathlib, subprocess, os
from itertools import product

root     = pathlib.Path(__file__).parents[1]          # project root
cfg      = json.load(open(root / "config.json"))
symbol   = cfg["symbol"]
start    = cfg["start"]
end      = cfg["end"]
cash     = str(cfg["cash"])
strategy = cfg["strategy"]

# ----- sweep grid ----------------------------------------------------------
periods    = [10, 20, 30]
devfactors = [1.5, 2.0, 2.5]
stakes     = [50, 100, 200]

outdir = root / "API" / "pnl_sweep" / symbol
outdir.mkdir(parents=True, exist_ok=True)

for p, d, s in product(periods, devfactors, stakes):
    outfile = outdir / f"pnl_{p}_{d}_{s}.json"
    cmd = [
        "python", str(root / "Backtester" / "backtest.py"),
        "--symbol", symbol,
        "--start",  start,
        "--end",    end,
        "--cash",   cash,
        "--period", str(p),
        "--devfactor", str(d),
        "--stake",  str(s),
        "--strategy", strategy,
        "--output", str(outfile),
    ]
    print("▶", " ".join(cmd))
    subprocess.run(cmd, check=True)

