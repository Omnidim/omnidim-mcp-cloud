import pytest
from httpx import AsyncClient

from app.config import get_settings

CHALLENGE_PATH = "/.well-known/openai-apps-challenge"


async def test_serves_the_configured_token_as_plain_text(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "openai_apps_challenge", "tok_abc123")

    res = await client.get(CHALLENGE_PATH)

    assert res.status_code == 200
    assert res.text == "tok_abc123"
    assert res.headers["content-type"].startswith("text/plain")
    assert res.headers["cache-control"] == "no-store"


async def test_is_not_found_while_no_token_is_configured(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(get_settings(), "openai_apps_challenge", "")

    res = await client.get(CHALLENGE_PATH)

    assert res.status_code == 404
