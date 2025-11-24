# DataPipeline/db.py
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

# Load .env variables (e.g. DB_PATH)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))


def resolve_db_path() -> Path:
    """Return an absolute path to the SQLite DB, with sensible defaults."""

    configured = os.getenv("DB_PATH")
    base_dir = Path(__file__).parent

    # If no env var is set, fall back to a local market_data.db in DataPipeline/
    if not configured:
        return base_dir / "market_data.db"

    # Support both relative (e.g. "market_data.db") and absolute paths
    candidate = Path(configured)
    return candidate if candidate.is_absolute() else base_dir / candidate


DB_PATH = resolve_db_path()

# Create the SQLite engine
engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)

# Create a configured session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
