import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

from app.db.session import Base
from app.models import *  # noqa: F403

# Test database URL (in-memory not supported for PostgreSQL, use local)
TEST_DATABASE_URL = "postgresql+asyncpg://vfs:vfs@localhost:5432/vfs_test"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create a clean database session for each test."""
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    from app.models.user import User

    user = User(id="test-user-001", email="test@vfs.ai", plan="free", credits=10)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
