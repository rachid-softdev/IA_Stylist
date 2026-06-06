import os

# Must be set BEFORE any app imports to ensure settings are loaded
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://vfs:vfs@localhost:5432/vfs_test")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-not-for-production")
os.environ.setdefault("CSRF_SECRET", "test-csrf-secret-not-for-production")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
import pytest_asyncio
import asyncpg
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql

from app.db.session import Base
from app.models import *  # noqa: F403

# Test database URL (in-memory not supported for PostgreSQL, use local)
TEST_DATABASE_URL = "postgresql+asyncpg://vfs:vfs@localhost:5432/vfs_test"
ASYNC_PG_DSN = "postgresql://vfs:vfs@localhost:5432/vfs_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=False, pool_size=5, max_overflow=5)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def _reset_schema():
    """Drop all tables and recreate them using raw asyncpg."""
    conn = await asyncpg.connect(ASYNC_PG_DSN)
    try:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(f'DROP TABLE IF EXISTS "{table.name}" CASCADE')
        pg_dialect = postgresql.dialect()
        for table in Base.metadata.sorted_tables:
            ddl = str(CreateTable(table).compile(dialect=pg_dialect))
            await conn.execute(ddl)
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a clean database session for each test."""
    await _reset_schema()
    # Dispose async engine connections to start fresh after DDL
    await engine.dispose()

    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    from app.models.user import User

    user = User(id="test-user-001", email="test@vfs.ai", plan="free", credits=10)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def client():
    """Create an async test client for the FastAPI app."""
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
