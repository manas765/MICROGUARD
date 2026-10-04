import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.models import AuditLog


@pytest.fixture
def db_session():
    """An isolated in-memory SQLite DB, with just the audit_log table
    created, for testing the audit module without touching the real
    Postgres database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine, tables=[AuditLog.__table__])
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()