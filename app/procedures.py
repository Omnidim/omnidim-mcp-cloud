"""MCP prompts (procedures) and resources (reference) for the cloud server.

The tools say WHAT can be called; these say which tool to call WHEN, in what
order, with which payload shape, and which gotchas to avoid. Mirrors the npm
server's procedure layer. Every step was proven against the live API before
being written down.
"""
from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path
from typing import Any

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
        else {"title": title, "readOnlyHint": False, "destructiveHint": False, "openWorldHint": True}
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
        "`requestDemo`. Never guess an answer. The `book_demo` prompt has the same steps.",
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

EXTRA_TOOLS: list[dict[str, Any]] = [_show_workflow_tool(), *_DEMO_TOOLS, *DOCS_TOOLS]

ROUTING_GUIDE = """# OmniDimension routing guide

OmniDimension is a voice AI platform. You create an **agent** (a.k.a. "bot"),
give it a **phone number** and optionally a **knowledge base**, then place
**calls** (one-off or as a bulk **campaign**) and read **call logs**.

## How to pick the right tool

- "Create / set up an agent that does X" -> the `provision_agent` prompt.
- "Why did calls fail / what happened on a call / summarize calls" -> the
  `audit_calls` prompt, then `listCallLogs` + `getCallLog`.
- "List / inspect what exists" -> `listAgents`, `listPhoneNumbers`,
  `listVoices`, `listKnowledgeBaseFiles`.
- "Get me a number / buy a number" -> `searchPhoneNumbers` { region, carrier }
  then `purchasePhoneNumber`. This spends the account's balance, so confirm the
  exact number and price with the user before buying. `releasePhoneNumber`
  gives one up and cannot be undone.
  `carrier` is required on both calls, in every region. Carriers do not stock
  the same numbers, so ask the user which one they want rather than picking:
  see the `omnidim://reference/carriers` resource for what each one stocks.
  `searchPhoneNumbers`'s response echoes the `carrier` a purchase must pass.
- "Place one call now" -> `dispatchCall`. "Call many contacts" -> the bulk
  call tools.
- "Book a demo / talk to the team", or a yes to a demo you offered -> the
  `book_demo` prompt: `getDemoQuestions`, `requestDemo`, then `bookDemo`.
  When to offer one: """ + DEMO_OFFER_RULE + """

## Rules that are easy to get wrong (proven against the live API)

1. **Write tools take flat top-level arguments.** `createAgent`,
   `updateAgent`, `attachPhoneNumber`, `dispatchCall`, etc. take their fields
   directly (e.g. `{ "agent_id": 1, "to_number": "+1..." }`). Do NOT wrap them
   in a `requestBody` object.
2. **Voices: use the `name` string as `voice_id`.** `listVoices` returns
   `id: null` for most voices; the usable identifier is the `name` field.
   Not every listed voice is synthesizable: an arbitrary one can produce a
   silent call. Prefer a known premade voice and confirm audio on a test call.
3. **The agent's numeric `voice` field is not used for speech.** It can read
   back as `false` on an API-created agent; that is normal. The call handler
   uses `voice_external_id` + `voice_provider`.
4. **Use the platform defaults:** transcriber `soniox`, one of the
   OmniDimension voices, model `gpt-4.1-mini`. Pick another provider only when
   the user names one. OmniDimension voices are our most recommended voices:
   picked by our team for each language and tested on real calls. List them
   with `listVoices` `provider=featured`, best first, and save one as
   `voice.provider` = its `service` (`cartesia`) with its `name` as
   `voice_id`. A Cartesia `search` does not find them. If none fits the
   language or tone, pick another `cartesia` voice.
5. **`dispatchCall` returning `success: true` does NOT mean a call
   connected.** It means the request was accepted. Proof of a real call is a
   resulting entry in `listCallLogs` whose `getCallLog` shows a non-empty
   `call_conversation`. Never treat the dispatch response as the outcome.
6. **Reading agents:** `getAgent` reports `voice: false`; read
   `voice_external_id` for the configured voice. `listAgents` puts the voice
   in the `voice` field. Do not report "no voice" from `getAgent.voice`.
7. **`listCallLogs` rows are large** and the response is trimmed if it grows
   past the size cap. Use a small `pagesize` (1-3) and fetch detail per row
   with `getCallLog`.
8. **Outbound `from_number_id`:** omit it to use the platform default number.
   A number that cannot reach the destination country yields an accepted
   dispatch but no connected call.
9. **IDs flow between calls:** `createAgent` -> `id` (the agent_id used
   everywhere downstream); `listPhoneNumbers` -> `id` (used as
   `phone_number_id` to attach and as `from_number_id` to dispatch).
10. **Phone numbers are E.164 with a leading `+`** everywhere.
11. **`voice.speech_speed` has a playable range per provider.** Default is
    `1.0`; only set it when the user wants faster/slower speech. For
    `eleven_labs` keep it within 0.7-1.2 (a value outside that produces a
    silent call, no error). `cartesia` accepts 0.6-1.5, `smallest-tts` 0.5-2.0.
12. **Cloning a voice: the user uploads the clip at
    https://omnidim.io/clone-voice.** A tool call cannot carry a real audio
    file: a 30 s clip is about 840,000 characters of Base64, too long to
    write out and corrupted by one wrong character. Send the user that link,
    then call `listClonedVoices` and wait for `status: ready`. Use its
    `voice_id` with `voice.provider: cartesia`. A `403` with
    `feature_not_enabled` or `permission_denied` on a voice tool means the
    user's plan or role has no voice cloning: tell them to upgrade or ask
    their administrator.
13. **Knowledge-base files over a few KB: the user uploads them at
    https://omnidim.io/files.** `uploadKnowledgeBaseFile` takes the PDF as
    Base64 in the call, so use it only for a small file. Then find the file
    with `listKnowledgeBaseFiles` and attach it with `attachKnowledgeBaseFiles`.
"""

_CREATE_AGENT_BLOCK = """2. Create the agent with `createAgent` (flat top-level fields):
   {
     "name": "<short name>",
     "welcome_message": "<for outbound, a name check of 8 words or fewer, e.g. Hi, am I speaking with [name]?>",
     "context_breakdown": [ { "title": "Purpose", "body": "<the agent's instructions, derived from the purpose above>" } ],
     "call_type": "Outgoing",
     "model": { "model": "gpt-4.1-mini", "temperature": 0.5 },
     "voice": { "provider": "cartesia", "voice_id": "<name from listVoices provider=featured>" },
     "transcriber": { "provider": "soniox" }
   }
   Before you write `welcome_message` and the instructions, read the
   `omnidim://guide/call-tips` resource: it lists what the best agents do on real calls.
   Capture the returned `id` as agent_id. (`status` is always "Completed"; it is not a build signal.)
3. Give it a number: `listPhoneNumbers` -> pick a number `id`. Attach it with
   `attachPhoneNumber` { phone_number_id, agent_id }. If no number exists,
   either buy one (`searchPhoneNumbers` { region, carrier } then
   `purchasePhoneNumber`, which charges the account, so confirm with the user
   first and never pick for them; `carrier` is required on both calls in every
   region, and carriers do not stock the same numbers) or import one you
   already own (importTwilioNumber / importExotelNumber / importSipTrunk).
4. Optional knowledge base: `uploadKnowledgeBaseFile` then `attachKnowledgeBaseFiles` { file_ids, agent_id }."""


def _provision_agent(args: dict[str, Any]) -> str:
    purpose = args.get("purpose") or "(describe the agent's job)"
    voice_id = args.get("voice_id")
    test_number = args.get("test_number")
    voice_line = (
        f'Use voice_id "{voice_id}" (the `name` from listVoices).'
        if voice_id
        else (
            "Start with the OmniDimension voices, our most recommended: call `listVoices` with "
            "`provider=featured` and pick the first one that speaks the caller's language. Use its "
            "`name` as voice_id and its `service` (`cartesia`) as the voice provider. Verify audio "
            "on the test call."
        )
    )
    if test_number:
        test_line = (
            f'5. Place a verification call with `dispatchCall` {{ agent_id, to_number: "{test_number}" }} '
            "(omit from_number_id to use the default outbound number). Capture the returned requestId.\n"
            f"6. Poll `listCallLogs` {{ pagesize: 1 }} until a new row appears for {test_number}, then `getCallLog` on "
            "its id. The call is verified ONLY if `call_conversation` is non-empty (the agent actually spoke). A "
            "successful dispatch response alone is not proof."
        )
    else:
        test_line = (
            "5. (No test_number given.) Tell the user the agent is configured and offer to place a verification call "
            "to a number they control. Until a call log shows a non-empty `call_conversation`, do not claim the agent "
            "works end to end."
        )
    return (
        f'Provision a working OmniDimension voice agent for this purpose:\n\n"{purpose}"\n\n'
        "Follow these steps in order. Write tools take flat top-level arguments (no `requestBody` wrapper).\n\n"
        f"1. Voice + models: {voice_line} A good default model is gpt-4.1-mini.\n"
        f"{_CREATE_AGENT_BLOCK}\n"
        f"{test_line}\n\n"
        "Throughout: phone numbers are E.164 with a leading `+`. See the `omnidim://guide/routing` resource for the "
        "full gotcha list."
    )


def _audit_calls(args: dict[str, Any]) -> str:
    focus = args.get("focus") or "(describe what to look into)"
    agent_id = args.get("agent_id")
    call_status = args.get("call_status")
    filters = ['"pagesize": 3']
    if agent_id:
        filters.append(f'"agentid": {agent_id}')
    if call_status:
        filters.append(f'"call_status": "{call_status}"')
    filter_str = ", ".join(filters)
    return (
        f'Audit OmniDimension call logs for this question:\n\n"{focus}"\n\n'
        f"1. List recent calls with `listCallLogs` {{ {filter_str} }}.\n"
        "   - Keep `pagesize` small (1-3). Each row is large and the response is trimmed past a size cap, so a big "
        "page comes back truncated and unparseable.\n"
        "   - Filters: `agentid` (note: no underscore) for one agent, `bulk_call_id` for one campaign, `call_status` "
        "for triage. The status enum uses a hyphen: completed | busy | failed | no-answer.\n"
        "   - Each row carries `id`, `call_status`, `sentiment_score`, cost, and a summary. There is no date-range "
        "filter; filter by `time_of_call` (MM/DD/YYYY HH:MM:SS) yourself if needed.\n"
        "2. For each call of interest, call `getCallLog` { call_log_id: <row id> } for the full transcript "
        "(`call_conversation`), `interactions`, `extracted_variables`, `recording_url`, and per-turn latency/cost. "
        "Note: an empty `call_conversation` means the agent never spoke (a silent call), not that the call is missing.\n"
        f'3. Summarize the answer to "{focus}": group by status or agent, surface failure reasons and low-sentiment '
        "calls, and cite specific `call_log_id`s.\n\n"
        "See the `omnidim://guide/routing` resource for the full gotcha list."
    )


def _restore_agent_version(args: dict[str, Any]) -> str:
    agent_id = args.get("agent_id") or "<agent_id>"
    goal = args.get("goal") or "(describe which earlier state you want back)"
    return (
        f'Roll agent {agent_id} back to an earlier version.\n\nGoal: "{goal}"\n\n'
        "Follow these steps in order. Do NOT restore blindly, preview first.\n"
        f"1. `listAgentVersions` {{ agent_id: {agent_id} }}. Versions come newest first; each has a "
        "`version_number`, `kind` (manual / auto / system), who saved it, when, and a `change_summary` "
        "(what changed in that version). Use the names, timestamps, and change summaries to find the one that "
        "matches the goal above. If version history is off for this org these calls return 403 "
        "(feature_disabled); report that and stop.\n"
        f"2. Preview the effect: `diffAgentVersion` {{ agent_id: {agent_id}, version_number: <chosen>, "
        'against: "current" }. This shows exactly what restoring that version WOULD change vs the agent\'s live '
        "config, grouped by area (Settings, Prompt, Transfer rules, etc.). If it reports no meaningful change, tell "
        "the user there is nothing to restore and stop. Show the user this preview and confirm before the next step.\n"
        f"3. Restore: `restoreAgentVersion` {{ agent_id: {agent_id}, version_number: <chosen> }}. This automatically "
        'saves the current state as a "Backup before restore" version first (so the restore is itself undoable), '
        "then writes the chosen config back. Check the response's `skipped` list: knowledge files or integrations "
        "that no longer exist are dropped and reported, not restored.\n"
        "4. Confirm: `listAgentVersions` again (a new system \"Backup before restore\" entry should be at the top) "
        "and tell the user they can undo by restoring it.\n\n"
        "See the `omnidim://guide/agent-versioning` resource for the full tool list and the diff `against` modes."
    )


def _build_outbound_campaign(args: dict[str, Any]) -> str:
    goal = args.get("goal") or "(describe who to call and why)"
    agent_id = args.get("agent_id")
    phone_number_id = args.get("phone_number_id")
    number_line = (
        f'Use phone_number_id "{phone_number_id}".'
        if phone_number_id
        else "Call `listPhoneNumbers` and pick the dialing number WITH the user; never pick silently."
    )
    agent_line = (
        f"Pass bot_id {agent_id} so this agent runs the calls even if the number has a different or no agent attached."
        if agent_id
        else "If the number has an agent attached it runs the calls; otherwise pass a `bot_id`."
    )
    return (
        f'Set up and launch an OmniDimension bulk-call campaign for this goal:\n\n"{goal}"\n\n'
        "Follow these steps in order. Write tools take flat top-level arguments (no `requestBody` wrapper).\n"
        "A campaign dials real people and spends real money: confirm the plan with the user before\n"
        "`startBulkCall`, and never start one they have not approved.\n\n"
        "1. Decide the shape: a one-time list is a normal campaign; continuously arriving leads mean a\n"
        "   dynamic campaign (`is_dynamic: true`) fed by `addBulkCallContact` instead of steps 3 and 5.\n"
        f"2. Number and agent: {number_line} {agent_line}\n"
        "3. Create it as a draft with `createBulkCall`\n"
        "   { name, phone_number_id, save_as_draft: true, concurrent_call_limit: <sized below> }.\n"
        "   Add `rotation` when dialing from several numbers (see the bulk-campaigns resource for the\n"
        "   shape). Keep the returned `id`.\n"
        "4. Size concurrency from the goal's numbers, not a guess: per channel, 3600 / average call seconds\n"
        "   gives calls per hour (~40 at 90s); divide the target hourly rate by that. Show the arithmetic\n"
        "   to the user.\n"
        "5. Add contacts with `addBulkCallContacts` in batches of up to 1000:\n"
        '   { bulk_call_id, contacts: [{ to_number: "+1...", custom_variables: {...} }] }.\n'
        "   This shape differs from create's contact_list on purpose; do not mix them. Report anything\n"
        "   that comes back in `rejected` with its row index. Each `custom_variables` key fills the\n"
        "   matching [placeholder] in the agent's greeting and prompt, so every row needs every key the\n"
        "   agent uses, or the agent says the placeholder out loud.\n"
        "6. Calling hours: if the goal names a time window, set it with `setBulkCallDailyTimeControl`\n"
        "   (both the stop and start blocks are required) and pass `daily_stop_timezone`/\n"
        "   `daily_start_timezone` for the customers' region; left out they fall back to the campaign's\n"
        "   timezone, and a mismatch dials people at night. Also set the agent's own `timezone` field\n"
        "   (`updateAgent`) so it works with the customers' local time on calls.\n"
        "7. Check the agent's greeting against the `omnidim://guide/call-tips` resource (a name check of\n"
        "   8 words or fewer loses far fewer calls in the first seconds). Suggest changes; never edit the\n"
        "   agent without the user's yes.\n"
        "8. Show the user the plan (campaign id, contact count, concurrency, window, rotation) and get\n"
        "   their explicit go-ahead. Then `startBulkCall`.\n"
        "9. Watch it: `getBulkCallLiveStatus` for progress. When it finishes, read per-contact outcomes\n"
        "   with `listBulkCallLines` (follow `next_cursor` until null) and offer `retryBulkCall` for\n"
        "   contacts that did not connect.\n\n"
        "See the `omnidim://guide/bulk-campaigns` resource for the full rules and failure modes."
    )


def _build_workflow(args: dict[str, Any]) -> str:
    goal = args.get("goal") or "(describe what should happen, and when)"
    return (
        f'Build an OmniDimension workflow for this goal:\n\n"{goal}"\n\n'
        "Read the `omnidim://guide/workflows` resource first. It explains triggers, outputs, ops and errors.\n\n"
        "1. Pick the trigger, then find each node type with `listWorkflowNodeTypes` and read its fields with\n"
        "   `getWorkflowNodeType`.\n"
        "2. For every field that takes an id (a number, template, integration or agent), list real choices with\n"
        "   `listWorkflowFieldOptions` and confirm them with the user. Never guess an id.\n"
        "3. `createWorkflow`, then build it with `editWorkflow` batches. Use readable node ids, wire branches with\n"
        "   `after` and `handle`, and add a notes node that says what the workflow is for.\n"
        "4. `validateWorkflow` and fix every error.\n"
        "5. A test run happens for real: messages, calls and CRM writes go out. Only call `testWorkflow` after the\n"
        "   user says yes, with their own phone number or email in the payload. It returns at once, so poll\n"
        "   `getWorkflowExecution` until `state` is `completed`, `failed` or `cancelled`.\n"
        "6. Show the user the finished flow, then `publishWorkflow` when they approve. Publishing makes it live.\n"
        "7. Prefer creating a new workflow. Never publish, activate, deactivate, delete or test an existing\n"
        "   workflow without the user's explicit yes, and read it with `getWorkflow` first.\n"
    )


def _book_demo(args: dict[str, Any]) -> str:
    return (
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
        "`requestDemo` again with the same answers and `after` set to `next_after`.\n"
        "6. Repeat the picked time and the answers back, get a yes, then call `bookDemo` with the "
        "same answers and `start_time` exactly as `requestDemo` returned it.\n"
        "7. Show everything `bookDemo` returns: the date and time in the user's timezone, how long "
        "it is, the join link (if it is empty, say the join link is in the calendar invite email), "
        "who is in the meeting (hosts and guests), when it was booked, and the reschedule and "
        "cancel links. Calendly sends the invite by email.\n"
        "8. If `bookDemo` returns 409 `slot_taken`, say that time was just taken and go back to "
        "step 5. If it returns 429, this account sent too many demo requests: ask them to wait a "
        "few minutes, and point them to their invite email if they already booked. If it fails any "
        "other way, do not call it again yourself: the booking may have gone through. Ask them to "
        "check their email for an invite, and book again only if they say none arrived."
    )


_PROMPTS: list[dict[str, Any]] = [
    {
        "name": "book_demo",
        "description": (
            "Book a demo call with the OmniDimension team: ask every booking question, route by "
            "call volume, offer free times, book the picked one, and show the meeting details."
        ),
        "arguments": [],
        "build": _book_demo,
    },
    {
        "name": "build_workflow",
        "description": (
            "Build an automation workflow from a plain-language goal: pick the trigger and nodes, wire them, "
            "validate, test with the user's consent, then publish."
        ),
        "arguments": [
            {"name": "goal", "description": "What should happen and when, in plain language (e.g. 'after a call, WhatsApp interested leads our follow-up template').", "required": True},
        ],
        "build": _build_workflow,
    },
    {
        "name": "provision_agent",
        "description": (
            "Create a working voice agent end to end: configure it, give it a number, and verify it can place a "
            "call and speak."
        ),
        "arguments": [
            {"name": "purpose", "description": "What the agent should do, in plain language (e.g. 'book dental appointments and answer FAQs').", "required": True},
            {"name": "voice_id", "description": "Optional voice name from listVoices. If omitted, use a known premade voice and confirm audio on the test call.", "required": False},
            {"name": "test_number", "description": "Optional E.164 number to place a verification call to after setup (e.g. +15551234567).", "required": False},
        ],
        "build": _provision_agent,
    },
    {
        "name": "audit_calls",
        "description": (
            "Review and summarize call logs: find failures, inspect transcripts and sentiment, or audit a specific "
            "agent or campaign."
        ),
        "arguments": [
            {"name": "focus", "description": "What to look into, in plain language (e.g. 'why are calls failing', 'summarize today's calls for agent 123').", "required": True},
            {"name": "agent_id", "description": "Optional agent id to filter to (the listAgents / createAgent id).", "required": False},
            {"name": "call_status", "description": "Optional status filter. Note the enum uses a hyphen for no-answer: completed | busy | failed | no-answer.", "required": False},
        ],
        "build": _audit_calls,
    },
    {
        "name": "build_outbound_campaign",
        "description": (
            "Set up and launch a bulk-call campaign safely: draft it, batch the contacts in, size concurrency "
            "from the numbers, check calling hours, then start and watch it."
        ),
        "arguments": [
            {"name": "goal", "description": "Who to call and why, in plain language (e.g. 'call 8,000 renewal leads today between 9 and 6 Eastern').", "required": True},
            {"name": "agent_id", "description": "Optional agent to run the calls (the listAgents id). If omitted, the agent attached to the chosen number runs them.", "required": False},
            {"name": "phone_number_id", "description": "Optional number id to dial from (from listPhoneNumbers). If omitted, pick with the user from their numbers.", "required": False},
        ],
        "build": _build_outbound_campaign,
    },
    {
        "name": "restore_agent_version",
        "description": (
            "Safely roll an agent back to an earlier saved version: find the right snapshot, preview exactly what "
            "restoring changes, then restore."
        ),
        "arguments": [
            {"name": "agent_id", "description": "The agent to roll back (the listAgents / createAgent id).", "required": True},
            {"name": "goal", "description": "What you want to get back to, in plain language (e.g. 'the version before I broke the transfer flow').", "required": False},
        ],
        "build": _restore_agent_version,
    },
]

RECOMMENDED_STACK = """# Recommended provider stacks

Each agent uses a transcriber (speech-to-text), a voice (text-to-speech), and a
language model, all set on `createAgent`. The pairings below work well in
production, grouped by the language your callers speak. Use `listSTTProviders`,
`listTTSProviders`, `listLLMProviders`, and `listVoices` for the live catalog.

## Language model

- Default: `gpt-4.1-mini` -- fast and accurate across languages, a good first
  choice for almost any agent.
- Alternatives: any other `name` from `listLLMProviders`, which lists only the
  models your organization can use.

## Voice

- Default: one of the OmniDimension voices, our most recommended voices. Our
  team picks them for each language and tests them on real calls. List them
  with `listVoices` `provider=featured`, best first, and save one under its
  `service` (`cartesia`). See `omnidim://reference/voices`.

## By caller language

- **Indian English (en-IN):** transcriber `soniox`; an OmniDimension voice
  for English (India).
- **Hindi / Hinglish (mixed Hindi and English):** transcriber `soniox`
  (handles code-mixed speech in one stream); an OmniDimension voice for Hindi.
- **Other Indian languages (Tamil, Telugu, Marathi, Bengali, Gujarati,
  Kannada, Malayalam, Punjabi):** transcriber `soniox`, or `sarvam` (tuned for
  Indian languages); an OmniDimension voice for that language.
- **US English:** transcriber `soniox` or `deepgram_stream`; an OmniDimension
  voice for English (American).
- **No OmniDimension voice for the language:** another `cartesia` voice.

## Field notes

- `transcriber.provider` is a `name` from `listSTTProviders`, which lists only
  the transcribers your organization can use. `deepgram_stream` also needs a
  `model` (`nova-3` or `nova-2`); the others do not.
- `voice.provider` is the `service` of a voice from `listVoices`, which lists
  only voices your organization can use. Send only `provider` and `voice_id`:
  the platform picks the voice model.

## Responsiveness

- Keep the system prompt focused. Long prompts add latency to every turn.
- Verify your chosen voice on a short test call before launch (see
  `omnidim://reference/voices`).
"""

VOICES_GUIDE = """# Choosing a voice

`listVoices` returns only the voices your organization can use. Use a voice's
`name` field as the `voice_id` and its `service` as the `voice.provider` you
pass to `createAgent`.

## Start with OmniDimension voices

OmniDimension voices are our most recommended voices. Our team picks them for
each language and tests them on real calls. Use one unless the user asks for
something else.

- List them with `listVoices` `provider=featured`. They come back best first.
- They cover English (India), English (American), Hindi, Tamil, Telugu,
  Marathi, Bengali, Gujarati, Kannada, Malayalam and Punjabi.
- Each one runs on Cartesia: save it as `voice.provider` `cartesia` with its
  `name` as `voice_id`.
- A Cartesia `search` does not find them. Only `provider=featured` lists them.

Example: Aadya, English (India) and Hindi, voice_id
`b521b304-7672-4cf9-9a34-b4eb1df1bde0`.

## If none fits

Pick another `cartesia` voice. `listVoices` `provider=cartesia` filters by
`search`, `language`, `accent` and `gender`. Not every catalog voice
synthesizes cleanly, so place a short test call and listen before launch.
"""

AGENT_CONFIG_GUIDE = """# Building an agent with createAgent

On this server `createAgent` takes flat top-level arguments (no `requestBody`
wrapper; see the routing guide). The fields:

- `name` -- agent name.
- `welcome_message` -- the first line the agent speaks.
- `context_breakdown` -- a list of `{ title, body }` sections that form the
  agent's instructions.
- `call_type` -- "Incoming" or "Outgoing".
- `model` -- `{ model, temperature? }`, e.g. `{ "model": "gpt-4.1-mini" }`.
- `voice` -- `{ provider, voice_id, speech_speed? }`. `speech_speed` is a playback
  multiplier (default `1.0`); leave it out unless the user asks for faster or
  slower speech. If you do set it, stay in the provider's playable range or the
  call goes silent: for `eleven_labs` keep it within **0.7-1.2** (sweet spot
  0.9-1.1) -- a value outside 0.7-1.2 produces no audio at all. `cartesia`
  accepts 0.6-1.5 and `smallest-tts` 0.5-2.0.
- `transcriber` -- `{ provider, model?, language? }`. `model` (`nova-3` /
  `nova-2`) is only needed for `deepgram_stream`.

## Example: Indian-English support agent (inbound)

{
  "name": "Support agent",
  "welcome_message": "Hi, thanks for calling. How can I help you today?",
  "context_breakdown": [
    { "title": "Role", "body": "You are a friendly customer-support agent. Answer questions, and if you cannot help, offer to connect the caller to a human." }
  ],
  "call_type": "Incoming",
  "model": { "model": "gpt-4.1-mini" },
  "voice": { "provider": "cartesia", "voice_id": "b521b304-7672-4cf9-9a34-b4eb1df1bde0" },
  "transcriber": { "provider": "soniox" }
}

## Example: Hindi / Hinglish appointment reminder (outbound)

{
  "name": "Appointment reminder",
  "welcome_message": "Namaste, kya aap [name] bol rahe hain?",
  "context_breakdown": [
    { "title": "Role", "body": "You remind customers about an upcoming appointment and confirm whether they can attend. Speak naturally in the caller's language, Hindi or English." }
  ],
  "call_type": "Outgoing",
  "model": { "model": "gpt-4.1-mini" },
  "voice": { "provider": "cartesia", "voice_id": "<a Hindi voice from listVoices provider=featured>" },
  "transcriber": { "provider": "soniox" }
}

Then give the agent a phone number and verify with a test call (the
`provision_agent` prompt walks through this end to end).
"""

VERSIONING_GUIDE = """# Agent version history

A **version** is a frozen snapshot of an agent's configuration at a point in
time. Use it to save a known-good setup before a risky change, and to roll back
if a change makes the agent worse.

## The tools

- `listAgentVersions` { agent_id } - the timeline, newest first. Each entry has a
  `version_number`, a `kind`, who saved it, and a `change_summary` (a one-line
  "what changed in this version vs the one before it").
- `createAgentVersion` { agent_id, name, note? } - save the agent's CURRENT
  config as a named version.
- `diffAgentVersion` { agent_id, version_number, against? } - what changed (below).
- `restoreAgentVersion` { agent_id, version_number } - write a version back onto
  the live agent.
- `renameAgentVersion` / `deleteAgentVersion` - tidy the timeline.

`kind` is `manual` (a person saved it), `auto` (saved automatically a few minutes
after editing settles - you do NOT trigger these), or `system` (a safety backup
taken automatically right before a restore).

## When to snapshot

Call `createAgentVersion` right BEFORE a change you might want to undo (swapping
the model/voice, rewriting the prompt, changing transfer rules). Give it a clear
`name`. You do not need to snapshot after routine edits - the platform auto-saves
settled states on its own.

## How to read a diff

`diffAgentVersion` returns `{ changed, groups }`, each group an area (Settings,
Prompt, Transfer rules, Post-call actions, Knowledge, Integrations, Web widget,
Conversation flow, Other settings) with the specific old -> new changes. Pick the
comparison with `against`:

- **omit / `against=previous`** (default): what changed IN this version vs the
  one before it. Matches the `change_summary` in the list.
- **`against=current`**: what restoring this version WOULD change vs the agent's
  live config right now. Read this before a restore to preview the effect.
- **`against=<number>`**: compare with a specific other version.

## How to decide and perform a restore

1. `listAgentVersions` and scan `change_summary` to find the target version.
2. `diffAgentVersion` { version_number, against: "current" } to preview exactly
   what restoring changes. If nothing meaningful changed, there is nothing to do.
3. `restoreAgentVersion` { agent_id, version_number }. This first saves the
   current state as a `system` "Backup before restore" version (so the restore is
   itself undoable), then writes the chosen config back. The response's `skipped`
   list reports references (knowledge files, integrations) that no longer exist
   and were dropped rather than failing the restore.
4. Confirm with `listAgentVersions` (a new `system` backup appears at the top).

## Gotchas

- Version history is enabled per organization. If it is off for the caller's org,
  these endpoints return 403 (`feature_disabled`).
- `createAgentVersion` refuses a no-op: if nothing changed since the latest
  version it returns 409 (`no_changes`). Make a real change first.
- There is a per-agent cap on versions created through the API; at the cap
  `createAgentVersion` returns 409 (`version_limit_reached`) - delete an old one.
- `listAgentVersions` and `diffAgentVersion` are read-only and safe to call
  freely. Restore and delete mutate the live agent - confirm intent first.
"""

BULK_CAMPAIGNS_GUIDE = """# Running outbound campaigns

## Normal or dynamic
- One-time list: a normal campaign. Create it (as a draft), add contacts, start it.
- Continuous leads (form fills, CRM events): a dynamic campaign (`is_dynamic: true`,
  no contact list) fed by `addBulkCallContact` as each lead arrives. The faster a
  fresh lead is called, the higher the conversion.

## The two contact shapes (do not mix them)
- `createBulkCall`'s `contact_list` rows are FLAT:
  `{ "phone_number": "+1...", "any_other_key": "reaches the agent as context" }`.
- `addBulkCallContact` / `addBulkCallContacts` instead take
  `{ to_number, custom_variables: {...}, metadata: {...} }`. `metadata` is
  bookkeeping the agent never sees.
- Sending `custom_variables` inside a `contact_list` row does not error; it becomes
  one nested variable and garbles the agent's context.

## Build as a draft, then start
- `createBulkCall` { name, phone_number_id, save_as_draft: true, ... }. Keep the
  returned `id`. Without `save_as_draft` the campaign dials the moment it is created.
- `addBulkCallContacts` accepts up to 1000 contacts per request. Invalid rows come
  back in `rejected` with their index and reason; valid rows are still added, so one
  bad number never costs the batch.
- `startBulkCall` launches a draft.
- Adding contacts is NOT dynamic-only: any campaign that is not cancelled or failed
  accepts them, and a completed campaign wakes up and dials again.

## Size concurrency with arithmetic, not vibes
- Calls per hour per channel = 3600 / average call seconds (~40/hour at 90s).
- Channels needed = target calls per hour / per-channel rate.
- Example: 100,000 calls in an 8-hour day is 12,500/hour, ~315 channels. The failure
  mode: concurrency 5 against 10,000 leads is ~200 calls/hour, a 50-hour "today"
  campaign.
- `setBulkCallConcurrency` changes it mid-run; the org's ceiling caps it.

## Numbers and rotation
- One number dialing a whole campaign collects spam reports and stops being answered.
  Rotate: `rotation: { numbers: [{ phone_number_id, sequence }], strategy:
  "fixed_count", calls_per_number: 50 }` at create.
- `phone_number_id` stays required and becomes the standby; list it in
  `rotation.numbers` too if it should take a share of the calls.
- A rotation number attached to a DIFFERENT agent is refused by name. Attach it to
  this campaign's agent first, or leave it out.
- `listBulkCallNumbers` shows which number is dialing now; `setBulkCallNumberActive`
  pauses one without losing its history (the last active number of a running
  campaign cannot be paused).
- Check a new number's reputation before a campaign and watch pickup rates.

## Calling hours and the timezone trap
- `setBulkCallDailyTimeControl` sets a hard stop and an auto start; the API requires
  both blocks together.
- Each block carries its own timezone (`daily_stop_timezone`, `daily_start_timezone`);
  left out, it falls back to the campaign's `timezone`, not the operator's. A wrong
  timezone dials people at 11 PM, which is a compliance problem. Set both to the
  customers' region.
- The agent has its own `timezone` field (`createAgent`/`updateAgent`) that sets the
  local date and time it works with during calls. Set that to the customers' region too.

## Watching a campaign and reading results
- `getBulkCallLiveStatus` for progress counts while it runs.
- `listBulkCallLines` for per-contact outcomes: `pagesize` up to 150, follow
  `next_cursor` until it comes back null, never build a cursor yourself.
  `include_total` once for a header, not on every page.
- Rows carry `recording_id`, not the transcript; `getCallLog` serves it.
- `retryBulkCall` re-queues contacts that did not connect; it refuses a campaign
  that is still running.

## Contact rules
- Numbers are E.164 with the country code. Run one campaign per country code.
- Dashboard CSV uploads need the phone column named exactly `phone_number`.
"""

CARRIERS_GUIDE = """# Which carrier to buy from

A region holds one or more carriers. They do not stock the same numbers and
they are not interchangeable, so `carrier` is **required** on
`searchPhoneNumbers` and `purchasePhoneNumber`, in every region, however few
it holds.

## What each one stocks

| Region | `carrier` | Stocks |
|---|---|---|
| `IN` | `carrier-1` | Landline numbers, city codes 11, 12 and 80 |
| `IN` | `carrier-2-new` | Mobile numbers, 94 and 79 series |
| `US` | `carrier-us` | US local numbers, by area code |

A snapshot, not the authority. The API is: omit `carrier` on a call that needs
one and the `409 carrier_required` body lists that region's carriers with what
each stocks and whether each is taking orders. Many MCP clients will not let
you omit a required field, which is why the table is here at all. If a user
names a carrier that is not in it, pass it through rather than refusing: this
file can be older than the account.

## Rules

- **Ask, do not pick.** Landline and mobile are not substitutes, and buying
  spends the account's balance on a rental that renews. If the user has not
  said which they want, ask, and say what each one stocks.
- **Buy from the carrier you searched.** `searchPhoneNumbers` echoes the
  `carrier` its results came from. Pass that exact value to
  `purchasePhoneNumber`, or you are buying out of inventory you never looked
  at.
- **Verification is per carrier.** An account verified on one carrier of a
  region is not verified on the other, and a purchase it has not cleared fails
  with `409 kyc_incomplete`. Verification is not on this surface: send the user
  to the dashboard number shop.
- **A carrier can be down.** One flagged unavailable is still named in the
  refusal, and a purchase against it answers `422 purchase_failed`. Sell from
  another one meanwhile.
- **The name is stable across a rename**, so it is safe for a user to store.
"""

WORKFLOWS_GUIDE = """# Building workflows

A workflow is a graph: one trigger node, then action and flow nodes joined by
edges. It runs on OmniDimension's servers each time its trigger fires.

## The tools, in the order you use them

1. `listWorkflowNodeTypes` (with `q`, e.g. "whatsapp") to find node types.
2. `getWorkflowNodeType` (`detail: minimal`) for the fields one type needs.
   Ask for `detail: full` only when you need the examples.
3. `listWorkflowFieldOptions` for any field of type `ref` (a number, an
   integration, a template, an agent). Never guess an id. If it returns
   `no_options`, ask the user for the value.
4. `createWorkflow` with a `name`. It starts with one node, `trigger`. You may
   pass a complete first `graph` instead, in the same shape `getWorkflow`
   returns under `draft` (node `config`, edges with `from`, `to`, `handle`).
5. `editWorkflow` with the `revision` from the last read and a list of `ops`.
6. `validateWorkflow`, then fix what it reports with another `editWorkflow`.
7. `testWorkflow` only after the user agrees (see "Test runs are real").
8. `publishWorkflow`. The workflow is live at once: real events run it. Do not call `activateWorkflow` after it.

`getWorkflow` with `view: structure` shows nodes and edges without config.
Use it to orient in a large workflow. Use `view: full` before you edit config.

## Lifecycle

- You always edit the **draft**. A published workflow is never changed in place.
- `publishWorkflow` copies the draft to the live version and leaves a fresh draft
  for the next round of edits. It refuses while `validateWorkflow` has errors.
- `deactivateWorkflow` pauses a published workflow. `activateWorkflow` resumes a paused one. Neither is
  needed to go live.
- Every edit needs the current `revision`. On `409 revision_conflict`, someone
  (often the user in the dashboard) saved first. Call `getWorkflow` and retry.

## Do not break a workflow that is already running

Most harm comes from changing a workflow the user did not ask you to touch.

- Default to creating a NEW workflow. Edit an existing one only when the user names it.
- Call `getWorkflow` first and read what it does before any edit. Keep its `revision`.
- Your edits land on the draft and change nothing live until you publish.
- `publishWorkflow` overwrites the live version that real events run. `deactivateWorkflow`
  pauses automation the user depends on. `deleteWorkflow` stops it for good. Before any of
  these on an existing workflow, tell the user exactly what will change and get a yes.
- Never publish, activate, deactivate, delete or test a workflow as a side effect of another task.

## Entry: the trigger

Every workflow has exactly one trigger node. Its output is the event payload,
which later nodes read as `{{ context.<trigger id>.<field> }}`.

| Trigger type | Fires when | How it is attached |
|---|---|---|
| `trigger` | After a call (post-call), or on a POST to the webhook URL | Post-call: the agent's post-call actions point at this workflow. Webhook: `update_node` the trigger with `config: { webhook_enabled: true }`, then `getWorkflow` returns `webhook_url` |
| `whatsapp_inbound` | A WhatsApp message arrives | Its `phone_number_id` |
| `twilio_sms_inbound` | An SMS arrives | Its Twilio integration |
| `email_event_trigger` | A sent email is opened, clicked, replied to, or bounces | The source workflow or campaign |
| `omnidim_crm_trigger`, `leadsquared_trigger`, `shopify_trigger`, `instantly_event_trigger` | An event in that system | Its integration |

`getWorkflowNodeType` shows each trigger's `output_example`. The post-call
trigger carries `customer_number`, `call_status`, `summary`, `sentiment`,
`extracted_variables` and the transcript.

## Connecting nodes

An edge runs from one node's **output** to the next node. Plain nodes have one
output, `default`. Branching nodes have named outputs, and you must say which.
`getWorkflowNodeType` lists each type's outputs; this table is a summary:

| Node | Outputs |
|---|---|
| `conditional` | `True`, `False` |
| `switch_condition` | each case `id`, plus `else` |
| `time_condition` | `Yes`, `No` |
| `photo_analyzer` | `pass`, `fail` |
| `voice_ai` | `Completed`, `Not Completed` |
| `zoho_bigin` | `Created`, `Found`, `Ambiguous`, `Failed`, `Success` |

- One output can feed several nodes. They all run.
- `add_node` with `after` and `handle` places and connects a node in one step.
- To rewire, send `disconnect` and `connect` in the same batch.
- Every node except notes must be reachable from the trigger.

## Exit

There is no end node. A branch ends at a node with no outgoing edge, and the
run finishes when every branch has ended. `wait`, `wait_for_time`, `voice_ai`
and `send_email` pause the run and resume it later. `sub_workflow` starts
another workflow and continues at once. The target must be published and active, or the run
fails with "Target workflow has no published version".

## Passing data

`{{ context.<node id>.<field> }}` reads an earlier node's output. The engine
also provides `{{ context.webhook }}` (the trigger payload) and
`{{ context.execution_link }}`. Only nodes that run earlier have output. A
reference to a later node renders empty, and `validateWorkflow` warns about it.

Node ids appear in these references, so pick readable ones: `check_interest`,
`wa_followup`, `notify_sales`. Use lowercase letters, digits and underscores.
These names are taken: `webhook`, `execution_id`, `execution_link`, `get`,
`items`, `keys`, `values`.

Id fields (a number, template, integration, agent) always hold a literal id.
A `{{ }}` template there is refused, because it could resolve to a record in
another workspace.

## Moving things around

- `move_node` sets `{x, y}` on the dashboard canvas.
- `add_node` without a `position` lands to the right of its parent, below any
  siblings, so the canvas stays readable for the user.

## Notes

A `notes` node holds `note_text` for people reading the canvas. It is never
connected and never runs. Add one that says what the workflow is for, so the
next person to open it in the dashboard understands it.

## Ops

| Op | Fields |
|---|---|
| `add_node` | `id`, `type`, `config?`, `label?`, `position?`, `after?`, `handle?` |
| `update_node` | `id`, `config` (merged; `null` removes a key), `label?` |
| `move_node` | `id`, `position {x, y}` |
| `delete_node` | `id` (its edges go too) |
| `connect` | `from`, `to`, `handle?` (default `default`) |
| `disconnect` | `from`, `to`, `handle?` |

A batch applies completely or not at all. A failing op returns
`422 invalid_op` with its `op_index`.

## Credentials

Never put secrets in config when an integration exists. Pick integrations,
numbers and templates from `listWorkflowFieldOptions`. Secret fields (a Slack
webhook URL, API headers) read back as `********`. Send `********` back
unchanged and the stored value is kept. If the user has no matching
integration, tell them to connect one in the dashboard first.

## Test runs are real

`testWorkflow` runs the draft once with your `payload` as the trigger data.
**Every node runs for real**: WhatsApp messages, SMS, emails and calls go out,
and CRM records change. Before you call it, tell the user what will happen and
get a yes. Use their own phone number or email in the payload. The call returns `202` with an
`execution_id` at once. Poll `getWorkflowExecution` until `state` is `completed`, `failed` or
`cancelled`, then read each node's status, output and error.

## Errors you will see

| Error | Meaning | What to do |
|---|---|---|
| `422 validation_failed` with `not_found` | An id is not in this workspace | Pick from `listWorkflowFieldOptions` |
| `422 validation_failed` on publish | Missing fields, an unconnected node, a bad handle | Fix each one, then publish again |
| `422 invalid_op` | An op is malformed | Fix the op at `op_index` |
| `409 revision_conflict` | The draft changed since you read it | `getWorkflow`, then retry |
| `409 no_draft` | There is no draft to edit, validate or publish | `getWorkflow`, then make an edit to start a new draft |
| `400 no_options` | The field holds an id from another system | Ask the user for the value |
| `422` with `templated_ref` | An id field holds a `{{ }}` template | Put a literal id from `listWorkflowFieldOptions` |

## Worked example

"After a call, if the lead is interested, send our follow-up WhatsApp template
and tell #sales in Slack."

1. `createWorkflow { name: "Interested lead follow-up" }` gives you `trigger`
   and a `revision`.
2. `listWorkflowFieldOptions` for `whatsapp.phone_number_id`, then for
   `whatsapp.template_id` with `depends` set to that number. Confirm both with
   the user.
3. One `editWorkflow` batch:
   - `add_node { id: "check_interest", type: "conditional", after: "trigger",
     config: { conditions: [{ variable: "{{ context.trigger.extracted_variables.interested }}",
     operator: "==", value: "yes" }] } }`
   - `add_node { id: "wa_followup", type: "whatsapp", after: "check_interest",
     handle: "True", config: { phone_number_id: <id>, message_type: "template",
     template_id: <id>, to_number: "{{ context.trigger.customer_number }}" } }`
   - `add_node { id: "notify_sales", type: "slack", after: "wa_followup",
     config: { slack_webhook_url: "<from the user>",
     message: "Follow-up sent to {{ context.trigger.customer_number }}" } }`
   - `add_node { id: "about", type: "notes", config: { note_text: "Follows up
     interested leads after a call." } }`
4. `validateWorkflow`, fix anything reported, then `publishWorkflow`.
5. Tell the user to point the agent's post-call action at this workflow.
"""

CALL_TIPS_GUIDE = """# Tips from real calls: what the best agents do

Where this comes from: answered calls in the 30 days to 20 November 2026, from
200 agents in 86 accounts (165 outbound agents in 79 accounts, 35 inbound
agents in 17), each with at least 100 answered calls. For each agent we took
two shares of its answered calls:

- **Early drop**: the person hung up within 15 seconds.
- **Natural end**: the agent ended or transferred the call when it was done.

The tables show the median agent in each group. Tips 1 and 5 come from these
numbers. The other tips come from reading calls of the agents with the fewest
early drops, and from the docs. None of this proves cause, so test a change
on a few calls before you roll it out.

## 1. Outbound: open with a name check of 8 words or fewer

| Outbound `welcome_message` length | Early drop | Natural end |
|---|---|---|
| 8 words or fewer | 31% | 26% |
| 9 to 15 words | 37% | 15% |
| 16 to 25 words | 49% | 15% |
| More than 25 words | 46% | 8% |

In 11 accounts that run outbound agents with both a short greeting (15 words
or fewer) and a longer one, the short one had fewer early drops in 10. A good
first line asks only for the person: "Hi, am I speaking with [name]?" Say who
you are and why on the next turn, after they answer.

Inbound is different: the caller chose to call. Inbound agents with a greeting
of 16 to 25 words had a median early drop of 19% (26 agents in 12 accounts).
Greet, say who they reached, and ask how you can help.

## 2. Outbound: on the second turn, say who, why, and ask for a minute

One sentence: the agent's name, the company, and the thing the person did,
such as "You asked about our evening course" or "You applied for the sales
role". Then ask for permission with a time: "Is now a good time for two
minutes?" If they are busy, ask when to call back, repeat the time, and end
the call politely.

## 3. Outbound: get past call screening

Many phones now answer unknown numbers with a screening assistant ("If you
record your name and reason for calling..."). Tell the agent to answer with
one sentence that holds its name, the company and the reason, then wait. If
the person says "please hold", the agent waits and does not repeat itself.

## 4. Fill in the person's details, and check every placeholder

Put variables in square brackets, like `[name]` or `[course]`. In a campaign
they come from the contact list columns, so each name must match a column
header, and every row needs a value. A missing value makes the agent say the
placeholder out loud.

## 5. Outbound: keep the temperature low for scripted calls

Outbound agents with `model.temperature` 0.3 or lower had a median early drop
of 37% and natural end of 21% (52 agents in 21 accounts), against 45% and 14%
at 0.3 to 0.7 (105 agents in 62 accounts). There were too few inbound agents
to tell.

## 6. One short question per turn

Ask one thing, then listen. Repeat back what you heard in a few words
("Got it, the evening slot") before the next question.

## 7. Speak the caller's language

Tell the agent to answer in the language the caller uses, and to keep the
words people really say for products and forms (often English terms inside
Hindi or another language). Pick the transcriber and voice from the
`omnidim://reference/recommended-stack` guide for that language.

## 8. End the call on purpose

Set `end_call` to `{ "enabled": true, "condition": "..." }` with a plain
condition, for example "End the call once the appointment is confirmed or the
person says they are not interested." Then the call ends when the job is done
instead of waiting for a silence timeout.

## What did not show a clear pattern

The language model, the prompt length and the speech speed showed no steady
difference once accounts with very different call types were compared. Pick
the model by language and cost (`omnidim://reference/recommended-stack`), and
keep `voice.speech_speed` near 1.0 unless the user asks for a change.

If something here is unclear, call `searchDocs`.
"""


_RESOURCES: list[dict[str, str]] = [
    {
        "uri": "omnidim://guide/routing",
        "name": "OmniDimension routing guide",
        "description": "Which tool to call when, ID flow between calls, and the non-obvious rules proven against the live API.",
        "mimeType": "text/markdown",
        "text": ROUTING_GUIDE,
    },
    {
        "uri": "omnidim://reference/recommended-stack",
        "name": "Recommended provider stacks by language",
        "description": "Which transcriber (STT), voice (TTS), and language model to choose, grouped by the caller's language. Reflects what works in production.",
        "mimeType": "text/markdown",
        "text": RECOMMENDED_STACK,
    },
    {
        "uri": "omnidim://reference/voices",
        "name": "Choosing a voice",
        "description": "Start with OmniDimension voices (listVoices provider=featured), our most recommended; how to save one, and what to pick when none fits.",
        "mimeType": "text/markdown",
        "text": VOICES_GUIDE,
    },
    {
        "uri": "omnidim://reference/agent-config",
        "name": "Building an agent with createAgent",
        "description": "The createAgent field shape with two complete, copy-ready example configurations (Indian-English support, Hindi/Hinglish reminder).",
        "mimeType": "text/markdown",
        "text": AGENT_CONFIG_GUIDE,
    },
    {
        "uri": "omnidim://guide/call-tips",
        "name": "Tips from real calls",
        "description": "What the best agents do on real calls: a short name-check greeting (measured), who and why on the second turn, call screening, placeholders, temperature (measured), ending calls.",
        "mimeType": "text/markdown",
        "text": CALL_TIPS_GUIDE,
    },
    {
        "uri": "omnidim://guide/bulk-campaigns",
        "name": "Running outbound campaigns",
        "description": "The campaign lifecycle end to end: draft, batch contacts (two contact shapes, do not mix), rotation, concurrency arithmetic, the agent-timezone trap, cursor-paged results.",
        "mimeType": "text/markdown",
        "text": BULK_CAMPAIGNS_GUIDE,
    },
    {
        "uri": "omnidim://reference/carriers",
        "name": "Which carrier to buy a number from",
        "description": "The carriers each region holds and what each one stocks, why `carrier` is required on search and purchase, and the rules that decide which to use: ask rather than pick, buy from the carrier you searched, verification is per carrier.",
        "mimeType": "text/markdown",
        "text": CARRIERS_GUIDE,
    },
    {
        "uri": "omnidim://guide/agent-versioning",
        "name": "Agent version history",
        "description": "How to save, diff, and restore agent config snapshots: which tool to call, what the diff `against` modes mean, how to decide on a restore, and the 403/409 gotchas.",
        "mimeType": "text/markdown",
        "text": VERSIONING_GUIDE,
    },
    {
        "uri": "omnidim://guide/workflows",
        "name": "Building workflows",
        "description": "How to build a workflow end to end: the tool order, lifecycle, triggers (entry), outputs and edges, exit, passing data, moving nodes, notes, ops, credentials, real test runs, errors, and a worked example.",
        "mimeType": "text/markdown",
        "text": WORKFLOWS_GUIDE,
    },
    {
        "uri": WORKFLOW_CANVAS_URI,
        "name": "Workflow canvas",
        "description": "Interactive view of a workflow draft, shown by clients that support MCP Apps.",
        "mimeType": "text/html;profile=mcp-app",
        "text": _WORKFLOW_CANVAS_HTML,
    },
]


def tool_meta(name: str) -> dict[str, Any] | None:
    if name == "showWorkflow":
        return {"ui": {"resourceUri": WORKFLOW_CANVAS_URI}}
    return None


def prompts_for_listing() -> list[dict[str, Any]]:
    return [{"name": p["name"], "description": p["description"], "arguments": p["arguments"]} for p in _PROMPTS]


def build_prompt(name: str, arguments: dict[str, Any]) -> dict[str, Any] | None:
    for p in _PROMPTS:
        if p["name"] == name:
            builder: Callable[[dict[str, Any]], str] = p["build"]
            return {
                "description": p["description"],
                "messages": [{"role": "user", "content": {"type": "text", "text": builder(arguments)}}],
            }
    return None


def resources_for_listing() -> list[dict[str, str]]:
    return [{k: r[k] for k in ("uri", "name", "description", "mimeType")} for r in _RESOURCES]


def read_resource(uri: str) -> dict[str, Any] | None:
    current = WORKFLOW_CANVAS_URI if uri == LEGACY_CANVAS_URI else uri
    for r in _RESOURCES:
        if r["uri"] == current:
            return {"contents": [{"uri": uri, "mimeType": r["mimeType"], "text": r["text"]}]}
    return None
