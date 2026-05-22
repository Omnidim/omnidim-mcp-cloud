# Changelog

## [Unreleased]

### Added

- FastAPI application scaffold with structured logging and a lifespan-managed database engine.
- Postgres schema for OAuth clients, authorization codes, access tokens, and refresh tokens. Token columns are hash-only.
- Discovery endpoints at `/.well-known/oauth-authorization-server` and `/.well-known/oauth-protected-resource`, including `authorization_response_iss_parameter_supported` and one-hour cache headers.
- Liveness and readiness probes at `/healthz` and `/readyz`. Readiness logs database failures.
- Request-ID middleware that binds a per-request identifier to log context and reflects it on the response.
- Multi-stage Dockerfile using a venv layout, non-root runtime user, configurable worker count, and built-in healthcheck.
- CI workflow running ruff, mypy, alembic migrations, pytest with coverage, and a container smoke test.
