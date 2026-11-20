"""Write Agent Skills (agentskills.io) from this server's prompts and guides.

    uv run python scripts/export_skills.py <out-dir>

One source: the skills are the same text the MCP prompts and resources serve, so they never drift
from the server. The Omnidim/skills repo holds the output.
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.procedures import _RESOURCES, build_prompt

_PREAMBLE = (
    "Needs the OmniDimension MCP server: hosted at `https://mcp.omnidim.io/mcp`, or local with "
    "`npx -y @omnidim-ai/mcp-server` (see the connect-omnidim skill). If a field, error or "
    "feature is unclear, call `searchDocs` before guessing.\n"
)

# (skill, description, [(prompt, arguments)], guides it always carries)
_SKILLS: list[tuple[str, str, list[tuple[str, dict[str, Any]]], list[str]]] = [
    (
        "build-agent",
        "Create an OmniDimension voice agent end to end: configure it, give it a phone number, "
        "test it with a real call, and roll it back to an earlier version if a change broke it. "
        "Use when the user wants a new voice agent, a bot for calls, or to undo agent changes.",
        [
            ("provision_agent", {"purpose": "what the user wants the agent to do"}),
            ("restore_agent_version", {"agent_id": "the agent id from listAgents"}),
        ],
        ["agent-config", "recommended-stack", "voices", "carriers", "agent-versioning"],
    ),
    (
        "build-workflow",
        "Build an OmniDimension automation workflow from a plain-language goal: pick the trigger "
        "and nodes, wire them, validate, test with consent, then publish. Use when the user wants "
        "something to happen automatically after a call or another event.",
        [("build_workflow", {"goal": "what should happen and when"})],
        ["workflows"],
    ),
    (
        "run-outbound-campaign",
        "Set up and launch an OmniDimension bulk-call campaign: draft it, add contacts in "
        "batches, size concurrency, check calling hours, then start and watch it. Use when the "
        "user wants to call a list of people.",
        [("build_outbound_campaign", {"goal": "who to call and why"})],
        ["bulk-campaigns", "carriers"],
    ),
    (
        "audit-calls",
        "Review OmniDimension call logs: find failed calls, read transcripts and sentiment, and "
        "summarize an agent or a campaign. Use when the user asks how calls went or why calls "
        "fail.",
        [("audit_calls", {"focus": "what the user wants to know about their calls"})],
        ["routing"],
    ),
]

_CONNECT = """\
---
name: connect-omnidim
description: "Connect an AI agent to an OmniDimension account through MCP, with the hosted server or a local one. Use when the OmniDimension tools are missing, a tool call fails with 401, or the user asks how to set OmniDimension up."
---

# Connect to OmniDimension

1. Hosted server, signs in with OAuth in the browser:
   - Claude Code: `claude mcp add --transport http omnidim https://mcp.omnidim.io/mcp`, then run `/mcp`.
   - Claude.ai, ChatGPT, Cursor and other clients: add `https://mcp.omnidim.io/mcp` as a custom connector.
   - For read access only, use `https://mcp.omnidim.io/mcp/readonly`.
2. Local server, uses an API key from https://omnidim.io/api-management:
   `npx -y @omnidim-ai/mcp-server setup` writes the key and the client config.
3. Check the connection with `getAccountBalance`. A 401 means the key or sign-in expired: sign in again or make a new key.

Guides for each client: https://docs.omnidim.io/docs/mcp. Call `searchDocs` for anything else.
"""  # noqa: E501 (frontmatter description is one line)

_REF_RE = re.compile(r"omnidim://(?:guide|reference)/([a-z0-9-]+)")


def _guides() -> dict[str, str]:
    return {m.group(1): r["text"] for r in _RESOURCES if (m := _REF_RE.fullmatch(r["uri"]))}


def _localize(text: str, prefix: str) -> str:
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
    (out / "connect-omnidim").mkdir(exist_ok=True)
    (out / "connect-omnidim" / "SKILL.md").write_text(_CONNECT)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    export(Path(sys.argv[1]))
