"""SQLite database setup via SQLModel."""

from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

# Ensure the data directory exists
db_path = settings.database_url.replace("sqlite:///", "")
Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, echo=False)


def init_db() -> None:
    """Create all tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: yield a DB session."""
    with Session(engine) as session:
        yield session
