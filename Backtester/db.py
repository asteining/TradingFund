# Backtester/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load the .env from DataPipeline/ which defines DB_PATH (e.g. "market_data.db")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../DataPipeline/.env"))

DB_PATH = os.getenv("DB_PATH")
if not DB_PATH:
    raise RuntimeError("DB_PATH not set. Ensure DataPipeline/.env exists and has DB_PATH.")

# Build the absolute path to the SQLite file under DataPipeline/
db_file = os.path.join(os.path.dirname(__file__), "../DataPipeline", DB_PATH)

engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
