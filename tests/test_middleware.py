import re

from httpx import AsyncClient


async def test_request_id_is_generated_when_absent(client: AsyncClient) -> None:
    res = await client.get("/healthz")
    assert res.status_code == 200
    assert "x-request-id" in res.headers
    assert re.fullmatch(r"[0-9a-f]{32}", res.headers["x-request-id"]) is not None


async def test_request_id_is_echoed_when_provided(client: AsyncClient) -> None:
    res = await client.get("/healthz", headers={"x-request-id": "test-id-12345"})
    assert res.status_code == 200
    assert res.headers["x-request-id"] == "test-id-12345"


async def test_each_request_gets_a_unique_id(client: AsyncClient) -> None:
    seen: set[str] = set()
    for _ in range(5):
        res = await client.get("/healthz")
        seen.add(res.headers["x-request-id"])
    assert len(seen) == 5
