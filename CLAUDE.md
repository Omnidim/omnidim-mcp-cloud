# CLAUDE.md — omnidim-mcp-cloud

Repo-specific rules for working on the hosted OmniDimension MCP service. Global rules in `~/.claude/CLAUDE.md` and workspace rules in `/Users/ryu/omnidim/CLAUDE.md` apply on top.

## What this repo is

The hosted FastAPI service at `mcp.omnidim.io`. Provides an OAuth 2.1 authorization server (for Claude.ai, ChatGPT, and other consumer-app MCP directories) and a Streamable HTTP MCP transport. State lives in a dedicated Postgres. Talks to Odoo over a small internal HTTP contract (`POST /api/internal/mint-scoped-key`, `POST /api/internal/revoke-key`).

Sibling repo `omnidim-mcp-server` is the npm-distributed local stdio variant; do not conflate the two.

## Test policy

**Every new feature ships with a test.** The CI gate is non-negotiable: ruff + mypy strict + alembic apply + every pytest must pass before any commit reaches `main`, and before any deploy.

- Tests live in `tests/`. Use `httpx.AsyncClient` with `ASGITransport(app=create_app())` for endpoint tests.
- Default suite: smoke tests for `/healthz`, `/readyz`, and both `.well-known` endpoints. These must always pass.
- Every new endpoint adds at least: a happy-path test, an auth-failure test, and a malformed-input test.
- DB-backed tests run against the Postgres service in CI. Local devs use `docker compose up -d postgres`.
- Migrations have their own test gate: `alembic upgrade head` must succeed from a fresh DB. Add a downgrade test when removing a field.

## URLs and copy that ship to users

Discovery endpoints and error responses are read by automated clients AND by humans inspecting them. Verify every external URL or instruction against actual product surfaces before writing it:

- API key management page: `https://omnidim.io/api-management`.
- Authentication docs: `https://docs.omnidim.io/docs/get-started/authentication`.

When in doubt, grep the docs repo (`omnidim-docs/content`) for the canonical path. Never invent.

## Architecture invariants

These do not bend without an explicit decision:

- **Stateless app servers.** All state in Postgres. No in-memory token caches, no session affinity, no local files.
- **Dedicated database.** Never share with Odoo's Postgres. A bug in this service must never take down voice calls.
- **Hash-only token storage.** `oauth_access_token`, `oauth_refresh_token`, `oauth_authorization_code`, and `oauth_client.client_secret` columns hold hashes, never plaintext.
- **PKCE S256 only.** No `plain` PKCE. Enforced at the DB level via CHECK constraint.
- **`asyncpg` for the app, `psycopg` for alembic offline mode.** Both ship with the package.
- **Logging is JSON over stdlib.** structlog with a stdlib bridge so uvicorn, gunicorn, and SQLAlchemy logs all land in the same pipeline. Loki ingests; no agent.

## Release flow

- `main` is the release branch. Every commit on `main` must pass CI.
- Production deploys on a `v*` git tag. The deploy job builds the image, pushes it to `ghcr.io/omnidim/omnidim-mcp-cloud`, then SSHes to the deploy host (`MCP_DEPLOY_*` secrets) to pull, migrate, restart, healthcheck, and roll back to the previous image on failure.
- Staging deploys on every merge to `main` once a staging host is provisioned.
- Never deploy from a laptop. Tag → CI → server.
- Database migrations are forward-compatible: an old app version must be able to run against the new schema for the rolling-deploy window.

## Changelog discipline

Every release gets an entry in `CHANGELOG.md` before its tag is pushed.

- Format: Keep a Changelog. Sections are `### Added`, `### Changed`, `### Fixed`, `### Removed`, `### Security` as needed.
- The `[Unreleased]` section collects entries as work lands on `main`. When tagging `vX.Y.Z`, rename that section to `[X.Y.Z] - YYYY-MM-DD` and start a fresh `[Unreleased]` above it.
- Entries describe user-visible behaviour, not commit-by-commit history. Group related commits into a single bullet.
- Breaking changes go under `### Changed` with a **BREAKING** prefix and a migration note.
- Security fixes belong in `### Security` with a CVE reference if one exists.
- If a tag goes out without an entry, that's a release process bug — fix it retroactively in the same release.

## Code hygiene

- Use SQLAlchemy for engine + migrations. For queries, prefer `session.execute(text("SELECT ..."))` so the SQL is readable in review. Full ORM idioms are allowed but not required.
- No marketing copy in user-facing strings. No "preserved", "intelligent", "powerful", em dashes, or fluff in commit messages, README copy, or in-code error messages.
- Comments only when the "why" is non-obvious. Single line if at all.
- Type hints required. `mypy --strict` is part of CI.

## Commits

- Conventional commit prefixes: `feat`, `fix`, `chore`, `docs`, `ci`, `build`, `test`, `refactor`.
- Single line. No body unless the change really needs one.
- No `Co-Authored-By` footer.
- Never run `git commit` without explicit user permission. Stage and summarise first, wait for the word "commit".
