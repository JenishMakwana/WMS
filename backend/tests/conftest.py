import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock, patch

import app.models  # noqa — register all models
from app.db.session import Base, get_async_session
from app.db.user_db import get_user_db
from fastapi_users.db import SQLAlchemyUserDatabase
from app.models.user import User
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_async_session():
    async with test_session_maker() as session:
        yield session


async def override_get_user_db():
    async with test_session_maker() as session:
        yield SQLAlchemyUserDatabase(session, User)


app.dependency_overrides[get_async_session] = override_get_async_session
app.dependency_overrides[get_user_db] = override_get_user_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def mock_send_email():
    with patch("app.services.user_manager.send_reset_password_email", new_callable=AsyncMock) as mock:
        yield mock


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
