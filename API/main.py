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
if db_path_env:
    DB_PATH = os.path.join(os.path.dirname(__file__), db_path_env)
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "../DataPipeline/market_data.db")

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




@app.get("/health")
def health_check():
    return {"status": "ok"}
