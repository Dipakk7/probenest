from sqlalchemy import inspect

from app.db.database import engine, init_db


def test_database_initialization() -> None:
    """Test SQLite database initialization and table creation."""
    init_db()
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "system_metadata" in tables
