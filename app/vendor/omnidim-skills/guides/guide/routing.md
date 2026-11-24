---
name: "OmniDimension routing guide"
description: "Which tool to call when, ID flow between calls, and the non-obvious rules proven against the live API."
---

# OmniDimension routing guide

OmniDimension is a voice AI platform. You create an **agent** (a.k.a. "bot"),
give it a **phone number** and optionally a **knowledge base**, then place
**calls** (one-off or as a bulk **campaign**) and read **call logs**.

## How to pick the right tool

- "Create / set up an agent that does X" -> the `design_agent` playbook, then
  the `provision_agent` playbook once the user approves the design.
- "Change / fix an agent" -> the `update_agent` playbook.
- "Why did calls fail / what happened on a call / summarize calls" -> the
  `audit_calls` playbook, then `listCallLogs` + `getCallLog`.
- "List / inspect what exists" -> `listAgents`, `listPhoneNumbers`,
  `listVoices`, `listKnowledgeBaseFiles`.
- "Get me a number / buy a number" -> `searchPhoneNumbers` { region, carrier }
  then `purchasePhoneNumber`. This spends the account's balance, so confirm the
  exact number and price with the user before buying. `releasePhoneNumber`
  gives one up and cannot be undone: release only after the user confirms
  that exact number.
  `purchasePhoneNumber` requires `carrier`. Pass the same `carrier` to the
  search, so you search the stock you buy from. Carriers do not stock the
  same numbers, so ask the user which one they want rather than picking:
  see the `omnidim://reference/carriers` resource for what each one stocks.
  `searchPhoneNumbers`'s response echoes the `carrier` a purchase must pass.
- "Place one call now" -> `dispatchCall`. "Call many contacts" -> the
  `build_outbound_campaign` playbook.
- "Book a demo / talk to the team", or a yes to a demo you offered -> the
  `book_demo` playbook: `getDemoQuestions`, `requestDemo`, then `bookDemo`.

## Rules that are easy to get wrong (proven against the live API)

1. **Write tools take flat top-level arguments.** `createAgent`,
   `updateAgent`, `attachPhoneNumber`, `dispatchCall`, etc. take their fields
   directly (e.g. `{ "agent_id": 1, "to_number": "+1..." }`). Do NOT wrap them
   in a `requestBody` object.
2. **Voices: use the `name` string as `voice_id`.** `listVoices` returns
   `id: null` for most voices; the usable identifier is the `name` field.
   Not every listed voice is synthesizable: an arbitrary one can produce a
   silent call. Start with the OmniDimension voices (rule 4) and confirm audio
   on a test call.
3. **The agent's numeric `voice` field is not used for speech.** It can read
   back as `false` on an API-created agent; that is normal. The call handler
   uses `voice_external_id` + `voice_provider`.
4. **Use the platform defaults:** transcriber `soniox`, one of the
   OmniDimension voices, model `gpt-4.1-mini`. Pick another provider only when
   the user names one. OmniDimension voices are our most recommended voices:
   picked by our team for each language and tested on real calls. List them
   with `listVoices` `provider=featured`, and save one as
   `voice.provider` = its `service` with its `name` as `voice_id`. A Cartesia `search` does not find them. If none fits the
   language or tone, pick another `cartesia` voice.
5. **`dispatchCall` returning `success: true` does NOT mean a call
   connected.** It means the request was accepted. Proof of a real call is a
   resulting entry in `listCallLogs` whose `getCallLog` shows a non-empty
   `call_conversation`. Never treat the dispatch response as the outcome.
6. **Reading agents:** `getAgent` and `listAgents` return the settings in
   other names and shapes than `createAgent` and `updateAgent` take (see the
   `omnidim://reference/agent-config` resource). Read the voice from
   `voice_external_id` and `voice_provider`, never from `voice`.
7. **`listCallLogs` rows are large** and the response is trimmed if it grows
   past the size cap. Scan with `include_details: false` and `pagesize` 5
   (even short rows are about 2.5 KB each), filter by `agentid`,
   `bulk_call_id` or `call_status`, then fetch each call you need with
   `getCallLog`.
8. **Outbound `from_number_id`:** run `listPhoneNumbers` first and pass the
   number the user picks. Omit it only when the account has no numbers: the
   platform default number is used then. A number that cannot reach the
   destination country yields an accepted dispatch but no connected call.
9. **IDs flow between calls:** `createAgent` -> `id` (the agent_id used
   everywhere downstream); `listPhoneNumbers` -> `id` (used as
   `phone_number_id` to attach and as `from_number_id` to dispatch).
10. **Phone numbers are E.164 with a leading `+`** everywhere.
11. **`voice.speech_speed` stays within 0.7-1.2.** Default is `1.0`; only set
    it when the user wants faster or slower speech. Outside that range some
    voices produce a silent call, with no error.
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
14. **A published agent keeps serving its published version.** If `getAgent`
    shows `published_state.is_published: true`, `updateAgent` and
    `restoreAgentVersion` change only the draft. Callers hear the change after
    the user publishes in the dashboard. There is no publish tool for agents.
