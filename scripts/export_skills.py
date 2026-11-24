from __future__ import annotations

import json
import re
import shutil
import sys
import tomllib
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.procedures import _RESOURCES, DEMO_OFFER_RULE, build_prompt

_REPO = Path(__file__).resolve().parents[1]
_USAGE = "uv run python scripts/export_skills.py <path to a clone of Omnidim/skills>"

_PLUGIN_DESCRIPTION = (
    "Build, test and update voice AI phone agents, place calls, run call campaigns, review call "
    "logs, and automate workflows and WhatsApp in your OmniDimension account."
)

_PREAMBLE = (
    "Needs the OmniDimension MCP server: hosted at `https://mcp.omnidim.io/mcp`, or local with "
    "`npx -y @omnidim-ai/mcp-server` (see the omnidim-connect skill). If a field, error or "
    "feature is unclear, call `searchDocs` before guessing.\n"
)

# (skill, description, [(prompt, arguments)], guides it always carries)
_SKILLS: list[tuple[str, str, list[tuple[str, dict[str, Any]]], list[str]]] = [
    (
        "omnidim-build-agent",
        "Design, build, test and change an OmniDimension voice agent: ask about the gaps and "
        "get the call script approved, build the full prompt and settings, give it a number, "
        "test it with a real call, apply fixes safely, and roll back if a change broke it. Use "
        "when the user wants a new voice agent, a bot for calls, to fix or change an agent, or "
        "to undo agent changes.",
        [
            ("design_agent", {"purpose": "<what the user wants the agent to do>"}),
            ("provision_agent", {"purpose": "<what the user wants the agent to do>"}),
            ("update_agent", {"change": "<which agent, and what to change>"}),
            (
                "restore_agent_version",
                {"agent_id": "<agent_id>", "goal": "<the earlier state the user wants back>"},
            ),
        ],
        ["agent-config", "recommended-stack", "voices", "carriers", "agent-versioning"],
    ),
    (
        "omnidim-build-workflow",
        "Build an OmniDimension automation workflow from a plain-language goal: pick the trigger "
        "and nodes, wire them, validate, test with consent, then publish. Use when the user wants "
        "something to happen automatically after a call or another event.",
        [("build_workflow", {"goal": "<what should happen and when>"})],
        ["workflows"],
    ),
    (
        "omnidim-run-campaign",
        "Set up and launch an OmniDimension bulk-call campaign: draft it, add contacts in "
        "batches, size concurrency, check calling hours, then start and watch it. Use when the "
        "user wants to call a list of people.",
        [("build_outbound_campaign", {"goal": "<who to call and why>"})],
        ["bulk-campaigns", "carriers"],
    ),
    (
        "omnidim-audit-calls",
        "Review OmniDimension call logs: find failed calls, read transcripts and sentiment, and "
        "summarize an agent or a campaign. Use when the user asks how calls went or why calls "
        "fail.",
        [("audit_calls", {"focus": "<what the user wants to know about their calls>"})],
        ["routing"],
    ),
]

_CONNECT = """\
---
name: omnidim-connect
description: "Connect an AI agent to an OmniDimension account through MCP, with the hosted server or a local one. Use when the OmniDimension tools are missing, a tool call fails with 401, or the user asks how to set OmniDimension up."
---

# Connect to OmniDimension

1. Hosted server, signs in with OAuth in the browser:
   - Claude Code: `claude plugin install omnidim --marketplace Omnidim/skills` adds the server and these skills. Then run `/mcp` to sign in. If your Claude Code does not know `--marketplace`, run `claude plugin marketplace add Omnidim/skills`, then `claude plugin install omnidim@omnidim`.
   - Claude.ai, ChatGPT, Cursor and other clients: add `https://mcp.omnidim.io/mcp` as a custom connector.
   - For read access only, use `https://mcp.omnidim.io/mcp/readonly`.
2. Local server, uses an API key from https://omnidim.io/api-management:
   `npx -y @omnidim-ai/mcp-server setup` writes the key and the client config.
3. Check the connection with `getAccountBalance`. A 401 means the key or sign-in expired: sign in again or make a new key.

Guides for each client: https://docs.omnidim.io/docs/mcp. Call `searchDocs` for anything else.
"""  # noqa: E501 (frontmatter description is one line)

_CLIENT_ONBOARDING = """\
---
name: omnidim-onboard-client
description: "Take a reseller's client on OmniDimension from nothing to a working phone number: create the account, fund it, verify it where the region requires it (India eKYC, US business checks), buy a number and attach it to an agent. Use when a reseller or agency onboards a new client, a client cannot buy a number because of KYC, or the user asks how to verify an account or set up a reseller client."
---

# Onboard a client

A reseller runs client accounts from its own product. This skill takes one client from nothing to a number it can call from, over the Reseller API. A runnable version of the same flow is at https://github.com/Omnidim/examples/tree/main/reseller-onboarding.

The MCP tools act on your own account. For a client, call the Reseller API at `https://omnidim.io/api/v1` with the reseller's key from https://omnidim.io/api-management, sent as `Authorization: Bearer <key>`. The key must belong to the account owner or an admin. Read it from an environment variable, never from the chat. A `403` on every reseller call means the account has no reseller access yet: it comes with the Reseller plan, granted on request at https://omnidim.io/contact-us?reason=reseller_api.

For your own account, not a client's, verification runs in the dashboard: https://docs.omnidim.io/docs/dashboard-guides/numbers-shop. The steps below are for resellers.

## Steps

1. **Create the client.** `POST /reseller/users/add` with `name`, `email`, `phone` and `password`. Optional: `cost_per_min` (at least what you pay) and `concurrent_call_limit`. Ask the user for every value, including the rate. Never invent a password or a price. Keep the `user_id` and `organization_id` from the response: verification, buying and attaching take `user_id`, and funding takes `organization_id`.
2. **Fund it.** A new client has no balance, so its calls cannot run. Preview with `POST /reseller/credits/calculate`, then `POST /reseller/credits/transfer` with `to_organization_id`, `minutes` and `cost_per_min`. This moves the reseller's money, so confirm the amount with the user first. A transfer takes no idempotency key: if it times out, read `GET /reseller/credits/logs` before you retry, or you may pay twice.
3. **Check whether the region needs verification.** `GET /reseller/kyc/status?user_id=<id>&region=<region>&carrier=<carrier>`. Read `kyc_required` first. Each entry in `regions` has the carrier's `status`, its `next_step` and `can_purchase`.
4. **Run the verification loop.** Post each step to `POST /reseller/kyc/steps/<next_step>` with `user_id`, `region`, `carrier` and that step's fields, and follow `next_step` from each response until there is none. `GET /reseller/kyc/requirements?region=<r>&carrier=<c>` lists every step's fields and formats. Branch on each step's `method`, never on its name:
   - `submit`: post the fields.
   - `otp`: post the code the client just received. Ask the client for it, and never store it. If no code arrived, call `resend-otp`.
   - `redirect`: send a `return_url`, which must be an https page in the reseller's own app. Give the client the single-use link to open in their own browser, then poll the step named in `poll_step`. The poll decides the result, not the page the client lands on. The link expires within minutes, so never store or reuse it.
   - `upload`: send the document as `multipart/form-data` in the field `document`. The step's `document` entry gives the accepted formats and size.
5. **Buy a number** on the carrier you verified. Search with `GET /phone_number/search?region=<r>&carrier=<c>&user_id=<id>`. Tell the user the number and its `monthly_rental_usd`, which is exactly what the purchase charges the client's balance each month, and wait for a yes. Then `POST /phone_number/purchase` with `region`, `carrier`, `phone_number` and `user_id`, and an `Idempotency-Key` header holding a fresh UUID. If the call times out, send it again with the same key: you get the first order back with `replayed: true` instead of a second charge.
6. **Attach the number** to one of the client's agents. The client needs an agent first. `POST /phone_number/attach` with `phone_number_id` (from the purchase response), `agent_id` and `user_id`.
7. **Optional:** issue the client its own API key, if its own system calls the API. The secret shows once.

## The carriers

| Carrier | Region | Stocks | Verification |
|---|---|---|---|
| `carrier-1` | IN | Landline, city codes 11, 12 and 80 | Codes by email and voice call, PAN, Aadhaar by OTP, preview, accept |
| `carrier-2-new` | IN | Mobile, 94 and 79 series | PAN, Aadhaar through a link, a document after each check, confirm |
| `carrier-us` | US | US local, by area code | Business details, address, authorized representative, confirm |

Don't rely on this table: a call without `carrier` returns `409 carrier_required` with the region's current carriers and what each stocks.

## Rules

- **`carrier` is required on every verification and number call.** Verification is per carrier. A client verified on one carrier must verify again on the other before it can buy there.
- **On `carrier-2-new`, `account_type` is permanent.** It is `individual` (the default) or `business`, set at `register`. A business sends `business_name` exactly as on its GST certificate. With no GST number, run `skip-gst` in place of `verify-gst`.
- **No `next_step` is not always done.** The US carrier ends in its own review: read the status again and report `review_status`. `refresh-review` asks where the review stands, about 30 seconds apart.
- **Never retry an Aadhaar or `redirect` step in a loop.** A rapid retry can lock the person out at the identity authority, and no API call undoes that. On `429 too_fast`, wait and ask the user before trying again.
- **You are relaying the client's personal data.** Never store or log the PAN, Aadhaar number, codes, GST number, the link or the documents.

## Errors

| Status | Slug | What to do |
|---|---|---|
| 400 | `invalid_request` | A field is missing or in the wrong shape. Check `/reseller/kyc/requirements` |
| 404 | `not_available` | This region can't be verified through the API |
| 409 | `step_order` | Run the step that `next_step` names first |
| 409 | `carrier_required` | Pick one of the carriers the response lists |
| 409 | `kyc_incomplete` | The client isn't verified on this carrier yet. Finish step 4 |
| 409 | `number_unavailable` | Someone took the number first. Search again |
| 402 | `insufficient_balance` | The client's balance can't cover the rental. Nothing was charged. Fund it first |
| 422 | `verification_failed` | The details or file were refused. Fix them with the client |
| 422 | `purchase_failed` | The client may or may not have been charged. Check its balance and numbers before any retry |
| 429 | `too_fast` | Wait about 30 seconds before retrying an Aadhaar step |
| 503 | `service_unavailable` | The verification service is down. Retry in a few minutes |

Field details: call `readDoc` on https://docs.omnidim.io/docs/reseller/your-clients/verification, or `searchDocs` for anything else.
"""  # noqa: E501 (frontmatter description is one line)

_REF_RE = re.compile(r"omnidim://(?:guide|reference)/([a-z0-9-]+)")


def _guides() -> dict[str, str]:
    return {m.group(1): r["text"] for r in _RESOURCES if (m := _REF_RE.fullmatch(r["uri"]))}


# MCP prompt names mean nothing to a skill user: point at the matching skill instead.
_PROMPT_SKILLS = {
    "design_agent": "the design steps of the omnidim-build-agent skill",
    "provision_agent": "the build steps of the omnidim-build-agent skill",
    "update_agent": "the update steps of the omnidim-build-agent skill",
    "restore_agent_version": "the omnidim-build-agent skill",
    "audit_calls": "the omnidim-audit-calls skill",
    "build_workflow": "the omnidim-build-workflow skill",
    "build_outbound_campaign": "the omnidim-run-campaign skill",
    "book_demo": "the demo booking steps",
}
_PROMPT_RE = re.compile(r"(?:the )?`([a-z_]+)` prompt")


def _localize(text: str, prefix: str) -> str:
    # The demo offer is a rule for the hosted server's sessions, not for a coding agent's skill.
    text = text.replace(f"\n  When to offer one: {DEMO_OFFER_RULE}", "")
    text = text.replace(DEMO_OFFER_RULE, "")
    text = _PROMPT_RE.sub(lambda m: _PROMPT_SKILLS.get(m.group(1), m.group(0)), text)
    return _REF_RE.sub(lambda m: f"{prefix}{m.group(1)}.md", text)


def _skill_body(prompts: list[tuple[str, dict[str, Any]]]) -> str:
    parts = []
    for name, args in prompts:
        built = build_prompt(name, args)
        assert built is not None, name
        parts.append(f"## {built['description']}\n\n{built['messages'][0]['content']['text']}")
    return "\n\n".join(parts)


def export(out: Path) -> None:
    guides = _guides()
    out.mkdir(parents=True, exist_ok=True)
    for skill, description, prompts, carried in _SKILLS:
        root = out / skill
        if root.exists():
            shutil.rmtree(root)
        (root / "references").mkdir(parents=True)
        body = _skill_body(prompts)
        # Carry every guide the text or another carried guide links to.
        needed, queue = set(carried), list(carried) + _REF_RE.findall(body)
        while queue:
            ref = queue.pop()
            needed.add(ref)
            queue += [r for r in _REF_RE.findall(guides[ref]) if r not in needed]
        refs = sorted(needed)
        for ref in refs:
            (root / "references" / f"{ref}.md").write_text(_localize(guides[ref], ""))
        links = "\n".join(f"- [{ref}](references/{ref}.md)" for ref in refs)
        (root / "SKILL.md").write_text(
            f"---\nname: {skill}\ndescription: {json.dumps(description)}\n---\n\n{_PREAMBLE}\n"
            f"{_localize(body, 'references/')}\n\n## References\n\n{links}\n"
        )
    (out / "omnidim-connect").mkdir(exist_ok=True)
    (out / "omnidim-connect" / "SKILL.md").write_text(_CONNECT)
    (out / "omnidim-onboard-client").mkdir(exist_ok=True)
    (out / "omnidim-onboard-client" / "SKILL.md").write_text(_CLIENT_ONBOARDING)


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n")


def export_plugin(root: Path) -> None:
    version = tomllib.loads((_REPO / "pyproject.toml").read_text())["project"]["version"]
    owner = {"name": "OmniDimension", "url": "https://omnidim.io"}
    _write_json(
        root / ".claude-plugin" / "plugin.json",
        {
            "name": "omnidim",
            "displayName": "OmniDimension",
            "version": version,
            "description": _PLUGIN_DESCRIPTION,
            "author": owner,
            "homepage": "https://docs.omnidim.io/docs/mcp",
            "repository": "https://github.com/Omnidim/skills",
            "license": "Apache-2.0",
            "privacyPolicyUrl": "https://omnidim.io/privacy-policy",
            "keywords": ["voice-ai", "phone-calls", "voice-agents", "call-campaigns", "workflows"],
        },
    )
    _write_json(
        root / ".claude-plugin" / "marketplace.json",
        {
            "name": "omnidim",
            "owner": owner,
            "description": _PLUGIN_DESCRIPTION,
            "plugins": [{"name": "omnidim", "source": "./", "description": _PLUGIN_DESCRIPTION}],
        },
    )
    _write_json(
        root / ".mcp.json",
        {"mcpServers": {"omnidim": {"type": "http", "url": "https://mcp.omnidim.io/mcp"}}},
    )
    shutil.copyfile(_REPO / "scripts" / "omnidim-icon.png", root / ".claude-plugin" / "icon.png")
    export(root / "skills")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(_USAGE)
    export_plugin(Path(sys.argv[1]))
