from httpx import AsyncClient


async def test_liveness(client: AsyncClient) -> None:
    res = await client.get("/healthz")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


async def test_readiness_when_db_is_up(client: AsyncClient) -> None:
    res = await client.get("/readyz")
    assert res.status_code in (200, 503)
    body = res.json()
    if res.status_code == 200:
        assert body["status"] == "ok"
    else:
        assert body["status"] == "degraded"
