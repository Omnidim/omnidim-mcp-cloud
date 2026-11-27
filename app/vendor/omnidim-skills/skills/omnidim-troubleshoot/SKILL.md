---
name: omnidim-troubleshoot
description: "Find why something in an OmniDimension account stopped working or works wrong, from the account's own data, and prove it with call ids. Use when the user says something used to work and now doesn't, 'since yesterday', a Google Sheet, webhook, CRM, Slack or email stopped getting call results, or asks why a call, agent or campaign behaved a certain way."
---

# Troubleshoot an OmniDimension account

If the OmniDimension tools are missing, connect the server: https://docs.omnidim.io/docs/mcp. If a field, error or feature is unclear, call `searchDocs` before guessing.

Read the playbook for the task and follow its steps in order. Fill each placeholder in quotes, parentheses or angle brackets from the user's request. Where a playbook names a playbook in the table below, open its file.

| Task | Playbook | Name |
|---|---|---|
| Anything that used to work and doesn't now, or works wrong: find what changed and prove the cause | [troubleshoot.md](troubleshoot.md) | `troubleshoot` |
| Call results not reaching a Google Sheet, webhook, CRM, Slack, email or another after-call action | [post-call-delivery.md](post-call-delivery.md) | `post_call_delivery` |
