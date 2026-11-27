---
name: staging-deploy
description: How omnidim-mcp-cloud deploys to staging. Use when asked to "deploy to staging", "push to the staging branch", when the Deploy staging run fails, when staging mcp-cloud serves an old commit, or when OmniOP on staging cannot reach mcp-cloud.
---

# Staging deploy

A push to the `staging` branch runs `.github/workflows/deploy-staging.yml` on the CodeBuild runner:

1. Starts Postgres 16 in docker, then `uv sync --locked --extra dev`, `ruff check .`, `mypy app`,
   `alembic upgrade head`, `pytest`. Any failure stops the run: no image.
2. Builds the Dockerfile and checks `/healthz` on the image.
3. Takes the role `github-deploy-staging-mcp-cloud` (var `STAGING_DEPLOY_ROLE_ARN` on the `staging`
   environment; only the `staging` branch may use it), pushes
   `559852958069.dkr.ecr.ap-south-1.amazonaws.com/staging/mcp-cloud:<sha>` (tags are immutable; a re-run
   skips an existing tag).
4. Runs SSM document `staging-deploy-mcp-cloud` on `i-0297d96cde2dddb67`, which runs
   `/srv/staging/deploy.sh mcp-cloud <sha>`: migrations, recreate, 30 s health, roll back on a crash.
   The run prints the document's output and fails unless it reports Success.

Merging into `staging` needs one approval (ruleset "Staging needs Alok or Kevin").
Prod is separate: release-please and `deploy.yml` on `v*` tags (see CLAUDE.md).

## Operate

- Change the box side (deploy.sh, compose.yml, role, document): omni-infra `staging/`
  (`deploy-roles.yaml` is stack `staging-deploy-roles`; its README has the other services).
- Verify: the run's last step shows deploy.sh's output for the sha; Run Command history in the staging
  account lists each `staging-deploy-mcp-cloud` run.
- Revert: merge a revert into `staging`, or rerun the workflow on an older commit (`workflow_dispatch`).
