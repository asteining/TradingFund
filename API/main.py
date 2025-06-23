# API/main.py
import os
import json
from typing import List

import pandas as pd
import pandas.errors as pderr

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .utils import current_cfg

cfg = current_cfg()

# ------------------------------------------------------------------
# 0. Environment / path setup
# ------------------------------------------------------------------
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

db_path_env = os.getenv("DB_PATH")
if not db_path_env:
    raise RuntimeError("DB_PATH must be set in API/.env")
DB_PATH = os.path.join(os.path.dirname(__file__), db_path_env)

# ------------------------------------------------------------------
# 1. FastAPI app + CORS
# ------------------------------------------------------------------
app = FastAPI(title="TradingFund API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# 2. Endpoints
# ------------------------------------------------------------------

@app.get("/spread_metrics")
def get_spread_metrics():
    """Return spread-backtest metrics stored in metrics_spread.json."""
    path = os.path.join(os.path.dirname(__file__), "metrics_spread.json")
    if not os.path.isfile(path):
        raise HTTPException(404, "metrics_spread.json not found")
    return json.load(open(path))


@app.get("/pnl", response_model=List[dict])
def get_pnl(
    symbol: str = Query(..., description="Ticker symbol used in the backtest"),
    strategy: str = Query(..., description="Strategy name used in the backtest"),
):
    """Return the P&L series for a given symbol & strategy."""
    fname = f"pnl_{symbol.lower()}_{strategy}.json"
    path = os.path.join(os.path.dirname(__file__), fname)
    if not os.path.isfile(path):
        raise HTTPException(404, f"{fname} not found — run the backtest first")
    return json.load(open(path))


@app.get("/seasonal_stats")
def seasonal_stats(symbol: str = cfg["symbol"]):
    path = os.path.join(os.path.dirname(__file__),
                        f"seasonal_stats_{symbol.lower()}.json")
    if not os.path.isfile(path):
        raise HTTPException(404, f"{path} not found")
    return JSONResponse(content=json.load(open(path)))


@app.get("/sweep_summary")
def sweep_summary(symbol: str = cfg["symbol"]):
    path = os.path.join(os.path.dirname(__file__),
                        f"sweep_summary_{symbol.lower()}.csv")
    if not os.path.isfile(path):
        raise HTTPException(404, f"{path} not found")
    df = pd.read_csv(path).where(pd.notnull(pd.read_csv(path)), None)
    return JSONResponse(content=df.to_dict(orient="records"))

@app.get("/health")
def health_check():
    return {"status": "ok"}
