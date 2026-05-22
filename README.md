# omnidim-mcp-cloud

OAuth 2.1 authorization server and Model Context Protocol transport for OmniDimension.

## Status

Pre-release. Discovery endpoints, schema, and lifecycle plumbing only.

## Local development

```bash
cp .env.example .env
docker compose up -d postgres
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then:

```bash
curl http://localhost:8000/healthz
curl http://localhost:8000/.well-known/oauth-authorization-server
```

## License

[Apache 2.0](./LICENSE)
