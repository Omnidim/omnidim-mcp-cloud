# Changelog

## [Unreleased]

## [0.2.4] - 2026-05-25

### Added

- `POST /api/telemetry/event` for anonymous usage events from the npm package companion. Validated against a strict schema; payload structlog-logged to Loki for observability dashboards.

### Security

- Upstream credentials stored at rest are now encrypted with Fernet, keyed off `TOKEN_SIGNING_KEY`.
- Structured log processor strips known-sensitive keys from every emitted event.

### Added

- `POST /mcp` Streamable HTTP transport (JSON-RPC 2.0). Bearer-token gated; supports `initialize`, `notifications/initialized`, `tools/list`, `tools/call`. WWW-Authenticate challenge on 401.
- Auto-generated tool registry from `omnidim-docs/openapi/omnidim.yaml` + shared `mcp-config.yaml` exclude list. 49 tools today. Drift-check via `app/_generated/.spec.yml`.
- `POST /revoke` (RFC 7009) — revokes the entire grant family.
- `refresh_token` grant on `POST /token` with one-time-use rotation + token-family revocation on replay.
- `GET /authorize` (OAuth 2.1 authorization endpoint; PKCE S256 required). Per-spec error handling: errors that can be safely reflected go via `redirect_uri` with `error` + `state`; client/redirect failures return JSON 400.
- `POST /token` (authorization code grant with PKCE verifier). Single-use codes, refresh token issued.
- `omnidim:all` is the supported scope. Missing `scope` on `/authorize` defaults to it.
- `python-multipart` runtime dependency for form-encoded `/token` requests.
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
