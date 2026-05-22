import os
from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://omni:omni@localhost:5433/omni_mcp")
os.environ.setdefault("PUBLIC_BASE_URL", "http://testserver")
os.environ.setdefault("DASHBOARD_BASE_URL", "http://localhost:3000")
os.environ.setdefault("ODOO_INTERNAL_BASE_URL", "http://localhost:8069")
os.environ.setdefault("ODOO_INTERNAL_SHARED_SECRET", "test-shared-secret")
os.environ.setdefault("TOKEN_SIGNING_KEY", "test-signing-key-padded-to-32-bytes!!")

from app.main import create_app


@pytest.fixture
async def app() -> AsyncIterator[FastAPI]:
    instance = create_app()
    async with instance.router.lifespan_context(instance):
        yield instance


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest.fixture
def session_factory(app: FastAPI) -> async_sessionmaker[AsyncSession]:
    return app.state.session_factory  # type: ignore[no-any-return]
