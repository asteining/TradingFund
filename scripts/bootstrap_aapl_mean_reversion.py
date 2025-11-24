"""Bootstrap utility to ensure the AAPL mean-reversion dataset exists.

Steps performed:
1) Load the shared config.json for symbol/start/end/strategy.
2) Download the symbol's OHLCV from Yahoo via DataPipeline helpers.
3) Write the slice to the shared SQLite DB.
4) Run the Backtester to produce API/pnl_<symbol>_<strategy>.json.

This script is safe to run multiple times; it will overwrite the existing
SQLite table and JSON output with fresh data.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from DataPipeline.pipeline import fetch_price_yahoo, save_to_db
from Backtester.backtest import run_backtest
CONFIG_PATH = ROOT / "config.json"
API_DIR = ROOT / "API"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config.json at {CONFIG_PATH}")
    return json.load(open(CONFIG_PATH))


def bootstrap():
    cfg = load_config()
    symbol = cfg.get("symbol", "AAPL").upper()
    strategy = cfg.get("strategy", "mean_reversion")
    start = cfg.get("start", "2020-01-01")
    end = cfg.get("end", datetime.today().strftime("%Y-%m-%d"))
    cash = float(cfg.get("cash", 100_000))

    print(f"Preparing dataset for {symbol} using {strategy} from {start} to {end}")

    # 1) Download the price history and persist to SQLite via DataPipeline helpers.
    try:
        df = fetch_price_yahoo(symbol, period="max")
    except Exception as exc:
        raise RuntimeError(
            "Failed to download prices from Yahoo Finance. Check network access and try again."
        ) from exc

    save_to_db(symbol, df, datetime.fromisoformat(start), datetime.fromisoformat(end))

    # 2) Run the backtest and emit the JSON P&L file the API expects.
    output_path = API_DIR / f"pnl_{symbol.lower()}_{strategy}.json"
    run_backtest(
        symbol=symbol,
        start=start,
        end=end,
        initial_cash=cash,
        output_json=str(output_path),
        strategy=strategy,
        period=20,
        devfactor=2.0,
        stake=100,
    )

    print(f"Bootstrap complete. JSON written to {output_path}")


if __name__ == "__main__":
    bootstrap()
