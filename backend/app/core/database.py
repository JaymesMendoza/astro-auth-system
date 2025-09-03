from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# SQLAlchemy setup
engine = create_engine(
    settings.database_url,
    # SQLite specific
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.environment == "development"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Database dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()