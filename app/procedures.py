"""MCP prompts (procedures) and resources (reference) for the cloud server.

The tools say WHAT can be called; these say which tool to call WHEN, in what
order, with which payload shape, and which gotchas to avoid. Mirrors the npm
server's procedure layer. Every step was proven against the live API before
being written down.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

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
- "Place one call now" -> `dispatchCall`. "Call many contacts" -> the bulk
  call tools.

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
4. **Set a transcriber** (e.g. `deepgram_stream` / `nova-3` / `en-US`).
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
"""

_CREATE_AGENT_BLOCK = """2. Create the agent with `createAgent` (flat top-level fields):
   {
     "name": "<short name>",
     "welcome_message": "<first line the agent speaks>",
     "context_breakdown": [ { "title": "Purpose", "body": "<the agent's instructions, derived from the purpose above>" } ],
     "call_type": "Outgoing",
     "model": { "model": "gpt-4.1-mini", "temperature": 0.5 },
     "voice": { "provider": "eleven_labs", "voice_id": "<voice name>" },
     "transcriber": { "provider": "deepgram_stream", "model": "nova-3", "language": "en-US" }
   }
   Capture the returned `id` as agent_id. (`status` is always "Completed"; it is not a build signal.)
3. Give it a number: `listPhoneNumbers` -> pick a number `id`. Attach it with
   `attachPhoneNumber` { phone_number_id, agent_id }. If no number exists,
   import one first (importTwilioNumber / importExotelNumber / importSipTrunk).
4. Optional knowledge base: `uploadKnowledgeBaseFile` then `attachKnowledgeBaseFiles` { file_ids, agent_id }."""


def _provision_agent(args: dict[str, Any]) -> str:
    purpose = args.get("purpose") or "(describe the agent's job)"
    voice_id = args.get("voice_id")
    test_number = args.get("test_number")
    voice_line = (
        f'Use voice_id "{voice_id}" (the `name` from listVoices).'
        if voice_id
        else (
            "Call `listVoices` and pick a premade voice; use its `name` as voice_id. "
            "Remember not every listed voice synthesizes, so verify audio on the test call."
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


_PROMPTS: list[dict[str, Any]] = [
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
]

RECOMMENDED_STACK = """# Recommended provider stacks

Each agent uses a transcriber (speech-to-text), a voice (text-to-speech), and a
language model, all set on `createAgent`. The pairings below work well in
production, grouped by the language your callers speak. Use `listSTTProviders`,
`listTTSProviders`, `listLLMProviders`, and `listVoices` for the live catalog.

## Language model

- Default: `gpt-4.1-mini` -- fast and accurate across languages, a good first
  choice for almost any agent.
- Alternatives: `gemini-2.5-flash`, `gpt-4o` (premium), `gpt-4.1-nano` (lighter).

## By caller language

- **Indian English (en-IN):** transcriber `azure_stream`; voice `cartesia`
  (default), `eleven_labs`, or `google`.
- **Hindi / Hinglish (mixed Hindi and English):** transcriber `soniox`
  (handles code-mixed speech in one stream); voice `cartesia` or `eleven_labs`.
- **Other Indian languages (Telugu, Bengali, etc.):** transcriber `soniox` or
  `sarvam` (tuned for Indian languages); voice `cartesia` or `sarvam`.
- **US / UK English:** transcriber `azure_stream` or `deepgram_stream`; voice
  `cartesia` or `eleven_labs`.

## Field notes

- `transcriber.provider` is one of `deepgram_stream`, `azure_stream`, `soniox`,
  `sarvam`, `cartesia`. `deepgram_stream` also needs a `model` (`nova-3` or
  `nova-2`); the others do not.
- `voice.provider` is one of `cartesia`, `eleven_labs`, `google`, `sarvam`.
  `cartesia` voices need a `model` such as `sonic-3.5`; for `eleven_labs` the
  model is implied by the voice.

## Responsiveness

- Keep the system prompt focused. Long prompts add latency to every turn.
- Verify your chosen voice on a short test call before launch (see
  `omnidim://reference/voices`).
"""

VOICES_GUIDE = """# Choosing a voice

`listVoices` returns the catalog. Use a voice's `name` field as the `voice_id`
you pass to `createAgent`. Quality varies by language and not every voice
synthesizes cleanly, so always place a short test call and listen before launch.

Filter `listVoices` by `provider` (`cartesia`, `eleven_labs`, `google`,
`sarvam`). ElevenLabs also supports `language`, `accent`, and `gender`.

By provider:

- **`cartesia`** -- low-latency multilingual voices; the platform default. Pass a
  `model` such as `sonic-3.5`. Example voice_id
  `bf0a246a-8642-498a-9950-80c35e9276b5` ("Sophie", English female).
- **`eleven_labs`** -- premium, expressive voices; the model is implied by the
  voice. Example voice_id `JBFqnCBsd6RMkjVDRZzb` ("George").
- **`sarvam`** -- natural prosody for Indian languages.
- **`google`** -- broad language coverage.
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
- `voice` -- `{ provider, voice_id, model? }`. `model` (e.g. `sonic-3.5`) is
  only needed for `cartesia`.
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
  "voice": { "provider": "cartesia", "model": "sonic-3.5", "voice_id": "bf0a246a-8642-498a-9950-80c35e9276b5" },
  "transcriber": { "provider": "azure_stream" }
}

## Example: Hindi / Hinglish appointment reminder (outbound)

{
  "name": "Appointment reminder",
  "welcome_message": "Namaste, main aapke appointment ke baare mein baat karne ke liye call kar rahi hoon.",
  "context_breakdown": [
    { "title": "Role", "body": "You remind customers about an upcoming appointment and confirm whether they can attend. Speak naturally in the caller's language, Hindi or English." }
  ],
  "call_type": "Outgoing",
  "model": { "model": "gpt-4.1-mini" },
  "voice": { "provider": "cartesia", "model": "sonic-3.5", "voice_id": "<pick one from listVoices>" },
  "transcriber": { "provider": "soniox" }
}

Then give the agent a phone number and verify with a test call (the
`provision_agent` prompt walks through this end to end).
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
        "description": "How to pick a voice from listVoices (use the name as voice_id), per-provider notes, and the verify-on-a-test-call rule.",
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
]


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
    for r in _RESOURCES:
        if r["uri"] == uri:
            return {"contents": [{"uri": r["uri"], "mimeType": r["mimeType"], "text": r["text"]}]}
    return None
