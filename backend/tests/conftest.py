"""Test fixtures and configuration for BloodTrace tests."""

import asyncio
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.config.database import get_db
from app.models.base import Base
from app.models.user_models import User, UserRole
from app.auth.security import get_password_hash, create_access_token

# Use SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_bloodtrace.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create and drop tables for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    """Provide a test database session."""
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    """Provide an async test client with overridden database dependency."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin test user."""
    user = User(
        email="admin@bloodtrace.test",
        name="Admin Test",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN.value,
        service="Administration",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def medecin_user(db_session: AsyncSession) -> User:
    """Create a medecin test user."""
    user = User(
        email="medecin@bloodtrace.test",
        name="Dr. Test",
        hashed_password=get_password_hash("medecin123"),
        role=UserRole.MEDECIN.value,
        service="Hematologie",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user: User) -> str:
    """Create a JWT token for the admin user."""
    return create_access_token(
        data={"sub": str(admin_user.id), "role": admin_user.role}
    )


@pytest_asyncio.fixture
async def medecin_token(medecin_user: User) -> str:
    """Create a JWT token for the medecin user."""
    return create_access_token(
        data={"sub": str(medecin_user.id), "role": medecin_user.role}
    )


def auth_headers(token: str) -> dict:
    """Create authorization headers from a token."""
    return {"Authorization": f"Bearer {token}"}
