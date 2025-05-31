# API/main.py

import os
import json
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    raise RuntimeError("DB_PATH must be set in API/.env")

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

@app.get("/pnl", response_model=List[dict])
def get_pnl():
    """
    Return the latest P&L series as a JSON list of {date: str, value: float}.
    For MVP, we’ll assume the backtester writes to API/pnl.json each time you run it.
    """
    pnl_json_path = os.path.join(os.path.dirname(__file__), "pnl.json")
    if not os.path.isfile(pnl_json_path):
        raise HTTPException(status_code=404, detail="PnL data not found. Run the backtest first.")
    with open(pnl_json_path, "r") as f:
        data = json.load(f)
    return data

@app.get("/health")
def health_check():
    return {"status": "ok"}
