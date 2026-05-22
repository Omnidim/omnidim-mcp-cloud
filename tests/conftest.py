import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://omni:omni@localhost:5432/omni_mcp")
os.environ.setdefault("PUBLIC_BASE_URL", "http://testserver")
os.environ.setdefault("DASHBOARD_BASE_URL", "http://localhost:3000")
os.environ.setdefault("ODOO_INTERNAL_BASE_URL", "http://localhost:8069")
os.environ.setdefault("ODOO_INTERNAL_SHARED_SECRET", "test-shared-secret")
os.environ.setdefault("TOKEN_SIGNING_KEY", "test-signing-key-padded-to-32-bytes!!")

from app.main import create_app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        async with app.router.lifespan_context(app):
            yield ac
