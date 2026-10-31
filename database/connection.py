"""
Async SQLAlchemy engine, session factory, and base model setup.
All database I/O in this application uses async/await throughout.
"""

from typing import Any, AsyncGenerator, Dict

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings


# -- Declarative base shared by all ORM models --------------------------------
class Base(DeclarativeBase):
    """Parent class for all SQLAlchemy models."""


# -- Engine - created once at module import -----------------------------------
_is_sqlite: bool = settings.DATABASE_URL.startswith("sqlite")
_engine_kwargs: Dict[str, Any] = {"echo": settings.DB_ECHO}
if not _is_sqlite:
    # Pool options are not valid for SQLite, so only apply them to other databases
    _engine_kwargs.update(
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,      # Verify connection health before use
        pool_recycle=3600,       # Recycle connections older than 1 hour
    )

engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

# -- Session factory - use as async context manager ---------------------------
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,      # Prevent lazy-load errors after commit
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields a database session per request.
    Commits on success, rolls back on any exception.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Create all tables defined in models on application startup.
    In production, use Alembic migrations instead.
    """
    # Import models so SQLAlchemy registers them before create_all
    from database import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_db() -> None:
    """Gracefully close all connections in the pool on shutdown."""
    await engine.dispose()