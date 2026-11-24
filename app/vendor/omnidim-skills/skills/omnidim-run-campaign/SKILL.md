---
name: omnidim-run-campaign
description: "Set up and launch an OmniDimension bulk-call campaign: draft it, add contacts in batches, size concurrency, check calling hours, then start and watch it. Use when the user wants to call a list of people."
---

# Run an OmniDimension call campaign

Needs the OmniDimension MCP server: hosted at `https://mcp.omnidim.io/mcp`, or local with `npx -y @omnidim-ai/mcp-server` (see the omnidim-connect skill). If a field, error or feature is unclear, call `searchDocs` before guessing.

Read the playbook for the task and follow its steps in order. Fill each placeholder in quotes, parentheses or angle brackets from the user's request. Where a playbook names a playbook in the table below, open its file. Where it names any other playbook or an `omnidim://` guide, read it with the `readGuide` tool.

| Task | Playbook | Name |
|---|---|---|
| Set up, start and watch a bulk-call campaign | [build-outbound-campaign.md](build-outbound-campaign.md) | `build_outbound_campaign` |
