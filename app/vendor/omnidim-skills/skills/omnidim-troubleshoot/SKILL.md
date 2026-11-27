---
name: omnidim-troubleshoot
description: "Find why something in an OmniDimension account stopped working or works wrong, from the account's own data, and prove it with call ids. Use when the user says something used to work and now doesn't, 'since yesterday', a Google Sheet, webhook, CRM, Slack or email stopped getting call results, or asks why a call, agent or campaign behaved a certain way, or wants to see what happened on a call (its events, timeline or profile). Also use when calls don't connect, don't ring or drop, a number stopped working, the agent is silent, slow, talks over callers or cuts off, a balance, charge, plan, GST invoice, renewal, auto-renew or released number is questioned, KYC is stuck, WhatsApp messages or templates fail, a dashboard screen or setting looks wrong or missing, a referral reward is pending or withheld, or the user asks for a feature the product may not have."
---

# Troubleshoot an OmniDimension account

If the OmniDimension tools are missing, connect the server: https://docs.omnidim.io/docs/mcp. If a field, error or feature is unclear, call `searchDocs` before guessing.

Read the playbook for the task and follow its steps in order. Fill each placeholder in quotes, parentheses or angle brackets from the user's request. Where a playbook names a playbook in the table below, open its file.

| Task | Playbook | Name |
|---|---|---|
| Anything that used to work and doesn't now, or works wrong: find what changed and prove the cause | [troubleshoot.md](troubleshoot.md) | `troubleshoot` |
| Call results not reaching a Google Sheet, webhook, CRM, Slack, email or another after-call action | [post-call-delivery.md](post-call-delivery.md) | `post_call_delivery` |
| Calls on a number don't connect, don't ring, drop, or never reach the agent | [calls-not-working.md](calls-not-working.md) | `calls_not_working` |
| A call sounds or behaves wrong: silence, slow replies, talking over the caller, cut off, wrong voice or sounds, or what happened on one call step by step | [call-audio-behavior.md](call-audio-behavior.md) | `call_audio_behavior` |
| Balance, charges, plan, GST, auto-renew or a released number | [billing.md](billing.md) | `billing` |
| A number isn't active or its KYC is stuck or rejected | [numbers-kyc.md](numbers-kyc.md) | `numbers_kyc` |
| WhatsApp messages fail, templates are missing or rejected, or replies don't reach the agent | [whatsapp.md](whatsapp.md) | `whatsapp` |
| A dashboard screen, feature or setting looks wrong or is missing | [dashboard-ui.md](dashboard-ui.md) | `dashboard_ui` |
| A referral reward is pending, withheld or missing | [referrals.md](referrals.md) | `referrals` |
| The user asks for a feature: what works today and the closest documented way | [feature-request.md](feature-request.md) | `feature_request` |
