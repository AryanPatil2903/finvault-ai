"""Shared pytest fixtures for FinVault AI test suite."""

import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.app import create_app
from database.connection import Base, get_db

TEST_DB_URL = "sqlite+aiosqlite:///./test_finvault.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()

from httpx import ASGITransport, AsyncClient

@pytest.fixture
async def client(db_session):
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
@pytest.fixture
async def auth_headers(client):
    await client.post("/api/v1/auth/register", json={
        "full_name": "Test User",
        "email": "test@finvault.com",
        "password": "testpass123",
        "monthly_income": 100000,
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "test@finvault.com",
        "password": "testpass123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}