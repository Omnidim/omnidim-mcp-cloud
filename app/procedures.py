"""MCP prompts (procedures) and resources (reference) for the cloud server.

The tools say WHAT can be called; these say which tool to call WHEN, in what
order, with which payload shape, and which gotchas to avoid. Mirrors the npm
server's procedure layer. Every step was proven against the live API before
being written down.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from app._generated.tools import TOOLS
from app.docs_tools import DOCS_TOOLS

# MCP Apps view; the HTML is the npm server's build output, copied unchanged.
_WORKFLOW_CANVAS_HTML = (Path(__file__).parent / "views" / "workflow_canvas.html").read_text()
# Where the canvas lived before its address carried a hash. Chats that showed it still ask for it there.
LEGACY_CANVAS_URI = "ui://omnidim/workflow-canvas"
# Chat apps cache a view by its address, so a changed page needs a new address or users keep the old one.
WORKFLOW_CANVAS_URI = (
    f"{LEGACY_CANVAS_URI}/{hashlib.sha256(_WORKFLOW_CANVAS_HTML.encode()).hexdigest()[:12]}"
)

_SHOW_WORKFLOW_DESCRIPTION = (
    "Show a workflow to the user as an interactive canvas in the chat, where they can move, "
    "rename, edit and delete nodes. Call it when the user asks to see a workflow, and once "
    "after you finish building or changing one. Do not call it before every edit: use "
    "`getWorkflow` to read the draft.\n\n(Tags: Workflows)"
)


def _show_workflow_tool() -> dict[str, Any]:
    # Same endpoint as getWorkflow; it exists so the canvas has one trigger, not one per build step.
    get = next(t for t in TOOLS if t["name"] == "getWorkflow")
    return {
        **get,
        "name": "showWorkflow",
        "description": _SHOW_WORKFLOW_DESCRIPTION,
        "input_schema": {
            "type": "object",
            "properties": {"workflow_id": get["input_schema"]["properties"]["workflow_id"]},
            "required": ["workflow_id"],
        },
        "query_params": [],
        "header_params": [],
        "annotations": {**get["annotations"], "title": "Show workflow canvas"},
    }


_DEMO_ANSWERS_SCHEMA: dict[str, Any] = {
    "name": {"type": "string", "description": "The person's full name."},
    "email": {
        "type": "string",
        "description": "Their work email. Personal addresses such as Gmail are refused.",
    },
    "timezone": {
        "type": "string",
        "description": (
            "The person's IANA timezone, e.g. Asia/Kolkata or America/New_York. Ask for it, and "
            "confirm any you work out from a city."
        ),
    },
    "guests": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Optional. More emails to invite.",
    },
    "answers": {
        "type": "object",
        "additionalProperties": {"type": "string"},
        "description": (
            "The answers to the `getDemoQuestions` questions with `source: calendly`, keyed by "
            "each one's `label`. Name, email and guests go in their own fields. For a choice "
            "question, use one of its `choices`, copied exactly. A phone number has its country "
            "code, like +14155550123. Only answers the user gave: never guess one."
        ),
    },
}


_DEMO_ANSWERS_REQUIRED = ["name", "email", "timezone", "answers"]


def _demo_tool(
    name: str,
    method: str,
    path: str,
    description: str,
    properties: dict[str, Any] | None = None,
    required: list[str] | None = None,
    *,
    title: str,
) -> dict[str, Any]:
    # A request or booking reaches the OmniDimension team, outside the user's account.
    annotations: dict[str, Any] = (
        {"title": title, "readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}
        if method == "GET"
        else {
            "title": title,
            "readOnlyHint": False,
            "destructiveHint": False,
            "openWorldHint": True,
        }
    )
    return {
        "name": name,
        "description": description + "\n\n(Tags: Demo)",
        "input_schema": {
            "type": "object",
            "properties": properties or {},
            "required": required or [],
        },
        "method": method,
        "path": path,
        "path_params": [],
        "query_params": [],
        "header_params": [],
        "annotations": annotations,
        # 502 booking_unconfirmed says not to retry; the generic 5xx hint says retry once.
        "relay_server_errors": True,
    }


# One text, used verbatim by the server instructions, the getDemoQuestions description and
# the routing guide. Clients defer tool descriptions, so only the instructions reach every
# session, and the three must never disagree.
DEMO_OFFER_RULE = (
    "Offer a demo call with the OmniDimension team once, in one sentence after you help "
    "with the task, when the user mentions thousands of calls a month, an enterprise or "
    "compliance need, white-label or reselling, a partnership, or pricing at their volume. "
    "Call getDemoQuestions only after they agree. If they decline or ignore the offer, "
    "do not offer again. Without one of these signals, do not offer it."
)

_DEMO_TOOLS: list[dict[str, Any]] = [
    _demo_tool(
        "getDemoQuestions",
        "GET",
        "/demo/questions",
        "Start booking a demo call with the OmniDimension team. Use it when the user asks for a "
        "demo or a call with the team, or agrees to one you offered. "
        + DEMO_OFFER_RULE
        + " Returns every question the booking asks, in "
        "order, with the allowed choices. Ask the user each one, plus their timezone, then call "
        "`requestDemo`. Never guess an answer. The `book_demo` playbook has the same steps.",
        title="Get demo booking questions",
    ),
    _demo_tool(
        "requestDemo",
        "POST",
        "/demo/request",
        "Send the user's answers. Confirm their phone number first: on the `ai_call` route a "
        "call goes to it. The server picks the route from their monthly call volume. "
        "`route: ai_call`: the request is filed. Tell the user the `message` and stop, without "
        "promising a meeting or a time. `route: calendar`: `slots` are free start times in UTC. "
        "Show some in the user's timezone with the day and date, and ask them to pick one. If "
        "none suit them or `slots` is empty, call again with `after` set to `next_after`. After "
        "three empty replies in a row, tell the user and stop. A 422 lists every answer to fix: ask only "
        "for those.",
        {
            **_DEMO_ANSWERS_SCHEMA,
            "after": {
                "type": "string",
                "description": "Optional. The `next_after` value from the last `requestDemo` reply, for later times.",
            },
        },
        _DEMO_ANSWERS_REQUIRED,
        title="Request a demo",
    ),
    _demo_tool(
        "bookDemo",
        "POST",
        "/demo/book",
        "Book the start time the user picked from `requestDemo`, with the same answers. Only after "
        "the user chose that time and confirmed the answers. Returns the meeting: start and end, "
        "join link, hosts, guests, when it was booked, the answers, and the reschedule and cancel "
        "links. Show the times in the user's timezone. Calendly emails the invite. 409 "
        "`slot_taken`: call `requestDemo` again with the same answers and no `after`, and offer "
        "other times. 429: too many demo requests from this account, wait a few minutes. Any "
        "other failure may still have booked it: do not call `bookDemo` again yourself. Ask the "
        "user to check their email for an invite, and book again only if they say none arrived.",
        {
            **_DEMO_ANSWERS_SCHEMA,
            "start_time": {
                "type": "string",
                "description": "The picked start time, exactly as `requestDemo` returned it.",
            },
        },
        [*_DEMO_ANSWERS_REQUIRED, "start_time"],
        title="Book a demo",
    ),
]


_BOOK_DEMO_STEPS = (
    "Book a demo call between the user and the OmniDimension team. Follow these steps in order.\n\n"
    "1. Call `getDemoQuestions`. Ask the user every question it returns, in that order. For a "
    "choice question, show the choices and use the exact text of the one they pick. If you "
    "already know their name or email, offer it and let them confirm. Ask for their timezone if "
    "you do not know it, and confirm it.\n"
    "2. Confirm their phone number, then call `requestDemo` with all the answers (`answers` "
    "keyed by each question's `label`). "
    "Never fill in an answer the user did not give.\n"
    "3. If it returns 422, ask again only for the fields it lists, then call `requestDemo` again.\n"
    "4. If `route` is `ai_call`: tell the user the `message` and stop. Do not promise a "
    "meeting or a time.\n"
    "5. If `route` is `calendar`: show 5 to 8 of the `slots`, converted to the user's timezone "
    "with the day and date. Ask them to pick one. If `slots` is empty or none suit them, call "
    "`requestDemo` again with the same answers and `after` set to `next_after`. After three empty "
    "replies in a row, tell the user and stop.\n"
    "6. Repeat the picked time and the answers back, get a yes, then call `bookDemo` with the "
    "same answers and `start_time` exactly as `requestDemo` returned it.\n"
    "7. Show everything `bookDemo` returns: the date and time in the user's timezone, how long "
    "it is, the join link (if it is empty, say the join link is in the calendar invite email), "
    "who is in the meeting (hosts and guests), when it was booked, and the reschedule and "
    "cancel links. Calendly sends the invite by email.\n"
    "8. If `bookDemo` returns 409 `slot_taken`, say that time was just taken, call `requestDemo` "
    "again with the same answers and no `after`, and go on from step 5 with the new slots. If it returns 429, this account sent too many demo requests: ask them to wait a "
    "few minutes, and point them to their invite email if they already booked. If it fails any "
    "other way, do not call it again yourself: the booking may have gone through. Ask them to "
    "check their email for an invite, and book again only if they say none arrived."
)


@dataclass(frozen=True)
class Playbook:
    name: str
    description: str
    arguments: list[dict[str, Any]]
    steps: str


@dataclass(frozen=True)
class Guide:
    uri: str
    name: str
    description: str
    text: str


_SKILLS = Path(__file__).parent / "vendor" / "omnidim-skills"
_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n+", re.S)


def split_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8-sig")
    match = _FRONTMATTER.match(text)
    if not match:
        raise ValueError(f"{path}: the header must sit between two --- lines")
    meta = yaml.safe_load(match.group(1))
    if not isinstance(meta, dict):
        raise ValueError(f"{path}: the header must be YAML keys")
    return meta, text[match.end() :]


def _playbook_file(path: Path) -> Playbook | None:
    if path.read_text(encoding="utf-8-sig").split("\n", 1)[0] != "---":
        return None
    meta, body = split_frontmatter(path)
    if "name" not in meta:
        raise ValueError(f"{path}: the header must give the playbook a name")
    title, steps = body.split("\n", 1)
    return Playbook(
        meta["name"], title.removeprefix("# "), meta.get("arguments", []), steps.strip()
    )


def load_playbooks(root: Path, reserved: frozenset[str] = frozenset()) -> dict[str, Playbook]:
    found: dict[str, Playbook] = {}
    for path in sorted(root.glob("skills/*/*.md")):
        playbook = None if path.name == "SKILL.md" else _playbook_file(path)
        if playbook is None:
            continue
        if playbook.name in found or playbook.name in reserved:
            raise ValueError(f"{path}: the playbook name {playbook.name} is already taken")
        found[playbook.name] = playbook
    return found


_BOOK_DEMO = Playbook(
    "book_demo",
    "Book a demo call with the OmniDimension team: ask every booking question, route by "
    "call volume, offer free times, book the picked one, and show the meeting details.",
    [],
    _BOOK_DEMO_STEPS,
)
_PLAYBOOKS: dict[str, Playbook] = {
    _BOOK_DEMO.name: _BOOK_DEMO,
    **load_playbooks(_SKILLS, reserved=frozenset({_BOOK_DEMO.name})),
}

_SERVER_ADDITIONS = {
    "omnidim://guide/routing": f"\n\n## Offering a demo call\n\n{DEMO_OFFER_RULE}",
}


def _guide_file(path: Path) -> Guide:
    meta, body = split_frontmatter(path)
    uri = f"omnidim://{path.parent.name}/{path.stem}"
    return Guide(
        uri, meta["name"], meta["description"], body.rstrip() + _SERVER_ADDITIONS.get(uri, "")
    )


_GUIDES: dict[str, Guide] = {
    g.uri: g
    for g in sorted(
        map(_guide_file, (_SKILLS / "guides").glob("*/*.md")),
        key=lambda g: (g.uri != "omnidim://guide/routing", g.uri),
    )
}

_CANVAS = {
    "uri": WORKFLOW_CANVAS_URI,
    "name": "Workflow canvas",
    "description": "Interactive view of a workflow draft, shown by clients that support MCP Apps.",
    "mimeType": "text/html;profile=mcp-app",
}

PLAYBOOK_NAMES: list[str] = list(_PLAYBOOKS)
GUIDE_NAMES: list[str] = PLAYBOOK_NAMES + list(_GUIDES)

_READ_GUIDE_TOOL: dict[str, Any] = {
    "name": "readGuide",
    "description": (
        "Read an OmniDimension playbook or guide. A playbook ("
        + ", ".join(PLAYBOOK_NAMES)
        + ") gives the steps for one task: read it before you start that task, then follow it. "
        "A guide is an `omnidim://` link that explains one topic: read it when a playbook or "
        "another guide points to it. It reads no account data.\n\n(Tags: Docs)"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "enum": GUIDE_NAMES,
                "description": "A playbook name, or a guide's omnidim:// link.",
            }
        },
        "required": ["name"],
    },
    "annotations": {
        "title": "Read a playbook or guide",
        "readOnlyHint": True,
        "destructiveHint": False,
        "openWorldHint": False,
    },
}

EXTRA_TOOLS: list[dict[str, Any]] = [
    _show_workflow_tool(),
    *_DEMO_TOOLS,
    *DOCS_TOOLS,
    _READ_GUIDE_TOOL,
]


_LINKS_NOTE = (
    "Where this text names a playbook or an `omnidim://` resource, read it with `readGuide`."
)
_PLAYBOOK_NOTE = (
    "Fill each placeholder in quotes, parentheses or angle brackets from the user's request. "
    + _LINKS_NOTE
)


def guide_text(name: str) -> str | None:
    if playbook := _PLAYBOOKS.get(name):
        return f"# {playbook.description}\n\n{_PLAYBOOK_NOTE}\n\n{playbook.steps}"
    if guide := _GUIDES.get(name):
        return f"{_LINKS_NOTE}\n\n{guide.text}"
    return None


def tool_meta(name: str) -> dict[str, Any] | None:
    if name == "showWorkflow":
        return {"ui": {"resourceUri": WORKFLOW_CANVAS_URI}}
    return None


def prompts_for_listing() -> list[dict[str, Any]]:
    return [
        {"name": p.name, "description": p.description, "arguments": p.arguments}
        for p in _PLAYBOOKS.values()
    ]


def build_prompt(name: str, arguments: dict[str, Any]) -> dict[str, Any] | None:
    playbook = _PLAYBOOKS.get(name)
    if playbook is None:
        return None
    values = {
        a["name"]: " ".join(str(arguments.get(a["name"]) or "").split()) for a in playbook.arguments
    }
    given = [f"- {name}: {value}" for name, value in values.items() if value]
    text = playbook.steps
    if given:
        text += "\n\nThe user gave:\n" + "\n".join(given)
    return {
        "description": playbook.description,
        "messages": [{"role": "user", "content": {"type": "text", "text": text}}],
    }


def resources_for_listing() -> list[dict[str, str]]:
    guides = [
        {"uri": g.uri, "name": g.name, "description": g.description, "mimeType": "text/markdown"}
        for g in _GUIDES.values()
    ]
    return [*guides, _CANVAS]


def read_resource(uri: str) -> dict[str, Any] | None:
    if guide := _GUIDES.get(uri):
        return {"contents": [{"uri": uri, "mimeType": "text/markdown", "text": guide.text}]}
    if uri in (WORKFLOW_CANVAS_URI, LEGACY_CANVAS_URI):
        return {
            "contents": [
                {"uri": uri, "mimeType": _CANVAS["mimeType"], "text": _WORKFLOW_CANVAS_HTML}
            ]
        }
    return None
