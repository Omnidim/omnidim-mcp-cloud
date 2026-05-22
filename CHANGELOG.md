# Changelog

## [Unreleased]

### Added

- `POST /register` Dynamic Client Registration endpoint (RFC 7591). MCP clients can register themselves to obtain a `client_id` and, for confidential clients, a one-time `client_secret`. Public clients (`token_endpoint_auth_method=none`) are the default and receive no secret.
- Strict redirect-URI validation: HTTPS only, loopback `http://localhost` and `http://127.0.0.1` allowed. URL fragments and userinfo are rejected.
- Cross-field validation per RFC 7591 §2: `authorization_code` grant requires `code` response type and vice versa; `refresh_token` grant requires `authorization_code`.
- RFC 7591 §3.2.2 error response shape for the OAuth surface: invalid input returns 400 with `{"error": "invalid_redirect_uri" | "invalid_software_statement" | "invalid_client_metadata", "error_description": "..."}` instead of the FastAPI default 422 envelope.
- Structured audit log entry on each successful registration. Never logs the plaintext secret, hash, or `software_statement`.
- FastAPI application scaffold with structured logging and a lifespan-managed database engine.
- Postgres schema for OAuth clients, authorization codes, access tokens, and refresh tokens. Token columns are hash-only.
- Discovery endpoints at `/.well-known/oauth-authorization-server` and `/.well-known/oauth-protected-resource`, including `authorization_response_iss_parameter_supported` and one-hour cache headers.
- Liveness and readiness probes at `/healthz` and `/readyz`. Readiness logs database failures.
- Request-ID middleware that binds a per-request identifier to log context and reflects it on the response.
- Multi-stage Dockerfile using a venv layout, non-root runtime user, configurable worker count, and built-in healthcheck.
- CI workflow running ruff, mypy, alembic migrations, pytest with coverage, and a container smoke test.
