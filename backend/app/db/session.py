from contextlib import contextmanager
from typing import Generator, Any

from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from app.core.config import settings

# Create the SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)

# Create a configured session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a scoped session for thread safety
ScopedSession = scoped_session(SessionLocal)

# Create a base class for declarative models
Base = declarative_base()


def get_session() -> Session:
    """Get a new database session."""
    return ScopedSession()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize the database by creating all tables."""
    # Import all models to ensure they're registered with Base
    from app.models import user, legal_section, mcq_question  # noqa

    Base.metadata.create_all(bind=engine)


def check_db_connected() -> bool:
    """Check if the database is connected."""
    try:
        # Try to connect and execute a simple query
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False