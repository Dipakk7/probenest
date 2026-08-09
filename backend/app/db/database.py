from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings
from app.core.logging import logger


class Base(DeclarativeBase):
    """Base model class for SQLAlchemy models."""


connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database tables and connections."""
    try:
        logger.info("Initializing database metadata...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Generator:
    """Dependency for obtaining database session in API routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
