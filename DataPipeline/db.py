# DataPipeline/db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

# Load .env variables (e.g. DB_PATH)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Expecting .env contains something like:
#    DB_PATH=/Users/ajs/Desktop/Coding Practice for Trading/TradingFund/DataPipeline/market_data.db
DB_PATH = os.getenv("DB_PATH")  # e.g. "market_data.db" or full path

if not DB_PATH:
    raise RuntimeError("Please set DB_PATH in DataPipeline/.env")

# Create the SQLite engine
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

# Create a configured session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
