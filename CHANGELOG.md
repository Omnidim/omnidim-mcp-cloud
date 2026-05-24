# Changelog

## [Unreleased]

### Added

- `GET /authorize`. Validates `client_id`, exact `redirect_uri` match, PKCE S256 challenge, and scope, then persists a single-use, hash-stored authorization request with a 10-minute TTL and redirects the browser to the dashboard consent screen. Client/redirect errors return 400 JSON (no redirect, per OAuth 2.1 §4.1.2.1); user-agent-safe errors redirect to the client's `redirect_uri` with `error` + `state`.
- `POST /token` (authorization code grant). Verifies PKCE, single-use code consumption, redirect-uri match, and client authentication; issues hashed access + refresh tokens that wrap the Odoo `user.api.key` id minted during consent.
- `POST /internal/issue-code` and `GET /internal/authorization-request/{id}`. Shared-secret-gated endpoints the consent screen uses to fetch a pending request's metadata and to issue the auth code after the user approves.
- Single coarse scope `omnidim:all`. Treats the grant as binary at consent time; missing `scope` on `/authorize` defaults to it rather than rejecting.
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
