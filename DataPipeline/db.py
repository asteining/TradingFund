import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

# Load .env variables (e.g. DB_PATH)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

def resolve_db_path() -> Path:
    """Return an absolute path to the SQLite DB, with sensible defaults and safe directory handling."""
    
    configured = os.getenv("DB_PATH")
    
    # Default fallback — use project root if no DB_PATH is set
    if not configured:
        fallback_path = Path("market_data.db")
    else:
        # Use absolute or relative path from env
        candidate = Path(configured)
        fallback_path = candidate if candidate.is_absolute() else Path(__file__).parent / candidate

    # Ensure parent directory exists (important for Render)
    fallback_path.parent.mkdir(parents=True, exist_ok=True)
    return fallback_path

# Resolve and construct DB path
DB_PATH = resolve_db_path()

# Create the SQLite engine
engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)

# Create a configured session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
