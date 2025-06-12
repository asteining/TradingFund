# API/main.py

import os
import json
from typing import List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

db_path_env = os.getenv("DB_PATH")
if not db_path_env:
    raise RuntimeError("DB_PATH must be set in API/.env")
DB_PATH = os.path.join(os.path.dirname(__file__), db_path_env)

# If you prefer to read directly from JSON, skip DB querying. But for flexibility, we’ll read JSON for now.
# In production, you might read the DB’s PnL table directly.

app = FastAPI(title="TradingFund API")

# Enable CORS so React (running on localhost:3000) can talk to this service on 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/spread_metrics")
def get_spread_metrics():
    """Return spread backtest metrics stored in metrics_spread.json."""
    metrics_path = os.path.join(os.path.dirname(__file__), "metrics_spread.json")
    if not os.path.isfile(metrics_path):
        raise HTTPException(status_code=404, detail="Spread metrics file not found")
    with open(metrics_path, "r") as f:
        data = json.load(f)
    return data

@app.get("/pnl", response_model=List[dict])
def get_pnl(
    symbol: str = Query(..., description="Ticker symbol used in the backtest"),
    strategy: str = Query(..., description="Strategy name used in the backtest"),
):
    """Return the P&L series for a given symbol and strategy."""
    filename = f"pnl_{symbol.lower()}_{strategy}.json"
    pnl_json_path = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.isfile(pnl_json_path):
        raise HTTPException(
            status_code=404,
            detail="PnL data not found. Run the backtest first.",
        )
    with open(pnl_json_path, "r") as f:
        data = json.load(f)
    return data

@app.get("/health")
def health_check():
    return {"status": "ok"}
