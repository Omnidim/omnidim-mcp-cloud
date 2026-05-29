# Changelog

All notable changes to this project. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.7] - 2026-05-29

### Fixed

- Agent and simulation tools that take an id in the path (`getAgent`, `updateAgent`, `deleteAgent`, `getSimulation`, `updateSimulation`, `deleteSimulation`) now reach the backend. The id was declared at the path-item level in the spec and the generator dropped it, so requests went to a literal `/agents/{agent_id}` and returned 404.
- `updateAgent` now documents its full input, including the nested `voice` object. Its request body was a schema reference the generator left unresolved, so the tool exposed no fields to set.

## [0.2.6] - 2026-05-27

### Changed

- Telemetry receiver accepts setup-funnel and crash events, including per-tool success and error counts, so install and runtime failures are diagnosable. Older clients keep working unchanged.

## [0.2.5] - 2026-05-25

### Added

- `POST /api/telemetry/event` accepts anonymous usage events from the npm package companion. Strict schema validation; payload structlog-logged to Loki.

## [0.2.4] - 2026-05-25

### Added

- Changelog entry for the telemetry endpoint shipped in 0.2.5.

## [0.2.3] - 2026-05-24

### Fixed

- structlog events are routed through stdlib so the Loki handler receives them.

## [0.2.2] - 2026-05-24

### Added

- Structured logs ship to Loki via `LOKI_PUSH_URL`. Labels configurable through `LOKI_LABELS`.

## [0.2.1] - 2026-05-24

### Security

- Upstream credentials at rest are encrypted with Fernet, keyed off `TOKEN_SIGNING_KEY`.
- Structured log processor strips known-sensitive keys (`api_key`, `access_token`, `refresh_token`, `client_secret`, `code_verifier`, `Authorization`) from every emitted event.

## [0.2.0] - 2026-05-24

### Added

- `POST /mcp` Streamable HTTP transport (JSON-RPC 2.0). Bearer-token gated. Supports `initialize`, `notifications/initialized`, `tools/list`, `tools/call`. Returns `WWW-Authenticate` challenge on 401.
- Auto-generated tool registry from `omnidim-docs/openapi/omnidim.yaml` plus a shared `mcp-config.yaml` exclude list. 49 tools today. Drift sentinel at `app/_generated/.spec.yml`.
- `POST /revoke` (RFC 7009). Revokes the entire grant family.
- `refresh_token` grant on `POST /token` with one-time-use rotation and grant-family revocation on replay.

## [0.1.0] - 2026-05-24

### Added

- OAuth 2.1 authorization server: `POST /register` (Dynamic Client Registration, RFC 7591), `GET /authorize` (PKCE S256 required), `POST /token` (authorization code grant with PKCE verifier). Single-use codes; refresh token issued at exchange. `omnidim:all` is the supported scope.
- Discovery endpoints `/.well-known/oauth-authorization-server` (RFC 8414) and `/.well-known/oauth-protected-resource` (RFC 9728), including `authorization_response_iss_parameter_supported` and one-hour cache headers.
- Strict redirect-URI validation: HTTPS only, with `http://localhost` and `http://127.0.0.1` allowed for loopback. URL fragments and userinfo are rejected.
- Cross-field validation per RFC 7591 §2: `authorization_code` grant requires the `code` response type and vice versa; `refresh_token` grant requires `authorization_code`.
- RFC 7591 §3.2.2 error response shape for the OAuth surface: invalid input returns 400 with `{"error": "...", "error_description": "..."}` instead of the FastAPI default 422 envelope.
- Structured audit log entry on each successful client registration. Never logs the plaintext secret, the hash, or `software_statement`.
- FastAPI application scaffold with structured logging and a lifespan-managed database engine.
- Postgres schema for OAuth clients, authorization codes, access tokens, and refresh tokens. Token columns are hash-only.
- Liveness and readiness probes at `/healthz` and `/readyz`. Readiness logs database failures.
- Request-ID middleware that binds a per-request identifier to log context and reflects it on the response.
- Multi-stage Dockerfile using a venv layout, non-root runtime user, configurable worker count, and built-in healthcheck.
- CI workflow running ruff, mypy, alembic migrations, pytest with coverage, and a container smoke test.
