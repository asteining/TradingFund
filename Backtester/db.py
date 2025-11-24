# Backtester/db.py

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load the .env from DataPipeline/ which defines DB_PATH (e.g. "market_data.db")
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../DataPipeline/.env"))


def resolve_db_path() -> Path:
    """Return an absolute DB path, defaulting to DataPipeline/market_data.db."""

    configured = os.getenv("DB_PATH")
    data_dir = Path(__file__).parent.parent / "DataPipeline"

    if not configured:
        return data_dir / "market_data.db"

    candidate = Path(configured)
    return candidate if candidate.is_absolute() else data_dir / candidate


DB_PATH = resolve_db_path()
engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
