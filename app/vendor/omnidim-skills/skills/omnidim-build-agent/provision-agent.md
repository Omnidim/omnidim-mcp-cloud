---
name: provision_agent
arguments:
  - name: purpose
    description: "What the agent should do, in plain language (e.g. 'book dental appointments and answer FAQs')."
    required: true
  - name: voice_id
    description: "Optional voice name from listVoices. If omitted, an OmniDimension voice for the agent's language is used."
    required: false
  - name: test_number
    description: "Optional E.164 number to place a verification call to after setup (e.g. +15551234567)."
    required: false
---

# Build a voice agent from its approved design: the full prompt and settings, a number, results after each call, and a test call to prove it speaks.

Build a production-ready OmniDimension voice agent for this purpose:

"(describe the agent's job)"

The source of truth is the call design the user approved with the `design_agent` playbook. If there is no approved design yet, run the `design_agent` playbook first. Build without one only if the user says to skip it, and then list your assumptions. The user's other material (documents, brochures, notes) only fills in facts the design already refers to, such as an exact spelling, an address, or a number the design names. It never changes behaviour, tone, flow, limits or approved lines. If the agent needs something neither gives, write [MISSING: what] and report it.

Follow these steps in order. Write tools take flat top-level arguments (no `requestBody` wrapper).

1. Conflict check. Show a table: conflict or gap | the design says | the material says | resolution. If there are none, write "No conflicts found." If a conflict changes the goal, a limit or price, the agent's identity, AI disclosure, legal claims or compliance, stop after the table and ask the user. Otherwise continue.
2. Write the prompt in the eight sections of the `omnidim://guide/agent-prompt` resource, one `context_breakdown` entry per section, with only the rules for the design's kind (**persuade**, **book**, **answer** or **survey**). Without a design, pick the kind from that resource's table and say which one you picked. Copy approved lines (welcome, objection replies, closings, voicemail) word for word. Put no fact marked [VERIFY] in the prompt: list each one as open. Before you write it, read the `omnidim://guide/call-tips` resource: it lists what the best agents do on real calls.
3. Welcome message: use the design's approved welcome word for word. Only without a design: If the user gave a welcome message, use it word for word. Otherwise, for an outbound call, write a name check of 8 words or fewer, such as "Hi, am I speaking with [name]?", and say who is calling and why on the next turn. For an inbound call, greet, say who they reached, and ask how you can help.
4. Voice and models: If the user named a voice, use it as voice_id (the `name` from listVoices). Otherwise start with the OmniDimension voices, our most recommended: call `listVoices` with `provider=featured` and pick one whose `featured_languages` include the primary language and whose `gender` matches the agent's voice gender. Use its `name` as voice_id and its `service` as the voice provider. If no voice has those fields, show the user a few names with their `sample_url` and let them pick. Leave out the model name so the organization's default model applies, unless the user names one, and set temperature 0.3. Transcriber `soniox`, or the one the `omnidim://reference/recommended-stack` resource gives for the caller's language. List every language the agent speaks in `languages`.
5. Create the agent with `createAgent`, setting only what the design uses:
   {
     "name": "<short name>",
     "welcome_message": "<from step 3>",
     "context_breakdown": [ { "title": "1. Identity and objective", "body": "..." }, "... one per section" ],
     "call_type": "Outgoing",
     "languages": ["<primary language>"],
     "model": { "temperature": 0.3 },
     "voice": { "provider": "<its service>", "voice_id": "<name from listVoices provider=featured>" },
     "transcriber": { "provider": "soniox", "should_apply_noise_reduction": true, "noise_reduction_mode": "advanced", "interruption_min_words": 3, "first_ideal_message": "<silence nudge>", "is_first_ideal_message_dynamic": false, "second_ideal_message": "<second nudge>", "is_second_ideal_message_dynamic": false },
     "end_call": { "enabled": true, "condition": "<when the call may end>", "message_type": "prompt", "message_prompt": "<a closing line for each outcome>" },
     "voicemail": { "enabled": true, "message": "<the voicemail line>" }
   }
   - `end_call.condition` lists when the call may end, from the kind's row in the `omnidim://guide/agent-prompt` table. For a **persuade** agent only, it also lists what is NOT a reason to end: a first no, "I'll think about it", "send me details", one-word replies. A stop request always ends the call. The closing lines and the silence nudges use the primary language, and the voice's gender if the language marks gender on verbs. The two `is_..._dynamic: false` flags make the agent say the nudges as written.
   - `languages` takes display names exactly as the dashboard's language picker shows them, such as "English (India)" or "Hindi". An unknown name is dropped without an error (all unknown is an error), and the order is not kept, so check the saved list in step 7.
   - Inbound: `call_type` "Incoming", and no `voicemail`. `voicemail` is for outbound calls only, and is an access-gated feature: ask the user whether voicemail is enabled for their account. If they do not know, leave `voicemail` out.
   - `transfer` only if the design has a handoff, with the same condition the prompt uses.
   Capture the returned `id` as agent_id. (`status` is always "Completed"; it is not a build signal.)
6. Self-check, and fix silently before you go on: every design decision is in the prompt; every branch has an instruction; approved lines are word for word; every fact traces to the design or the material; no rule appears twice and no two rules contradict; every example follows the script rules; the end-call condition matches the prompt's ending list; the welcome, voicemail, nudges and closing lines match the identity, and the voice's gender if the language marks gender on verbs; every tool in section 6 is attached; the AI disclosure rule and the identity do not contradict; the result variables cover every outcome. Fix anything you find with `updateAgent`, and send the full `context_breakdown` list: it replaces every section with the list you send.
7. Fetch it back with `getAgent` and check every setting saved, reading the names the `omnidim://reference/agent-config` resource maps (`getAgent` returns them flat: `voice_external_id`, `languages` labels, `asr_service`, `llm_temperature`, `is_end_call_enabled`, `end_call_message_type`, `voicemail_enabled`, `first_ideal_message`). Fix or report each mismatch.
8. Tools and knowledge, as the kind needs. The agent can only do what an attached tool does: without one it can only promise a follow-up.
   - Booking (**book** agents, or a booking step in another kind): run `listIntegrations`. A `google_calendar`, `calendly` or `cal` integration gives the agent tools to fetch free slots and book during the call. `calendly` and `cal` also need the caller's email, and `calendly` may ask its own booking questions: put them in the prompt's book steps. Calendars are connected in the dashboard at https://omnidim.io/integration: if the user has none, send them there, then list again.
   - The user's own system (a booking API, an order lookup, a CRM): `createCustomApiIntegration` with the endpoint the user gives. Its `description` says what it returns and when the agent should call it. Set `isLLMGenerated: true` on each value the caller says. Ask the user for the URL, headers and keys: never invent them.
   - Attach each tool the user confirms with `agentIntegrationActions` { action: "attach", agent_id, integration_id }, and check that section 6 of the prompt has its one line.
   - Reference material over about a page (price lists, menus, policies), mostly for **answer** agents: the user uploads it at https://omnidim.io/files (`uploadKnowledgeBaseFile` only for a small file). Attach it with `agentKnowledgeBaseActions` { action: "attach", file_ids, agent_id, `when_to_use` }, where `when_to_use` says which questions the file answers.
   - If a tool the design needs cannot be connected now, build with the follow-up line ("the team will confirm your slot"), and list the missing tool in the final reply.
9. Results after each call: `addPostCallAction` { agent_id, type: "omni_crm" (or where the design sends them; ask the user if unsure), include: ["summary", "sentiment", "fullConversation", "extracted_variables"], extracted_variables: [ { key, prompt } ] }. Variables for every kind: call_status (the design's outcomes), callback_time, do_not_call, language_used, asked_if_ai, and one per question the agent asks. Then by kind:
   - **persuade**: goal_confirmed (yes only on explicit agreement), hot_lead, objection_raised (the design's objection list), not_interested_reason.
   - **book**: booking_status (booked, rescheduled, cancelled or not booked, from the tool's answer only), booking_time.
   - **answer**: resolved (yes or no), topic, transferred.
   - **survey**: survey_complete (yes or no), plus the one per question above.
   Each prompt lists its allowed values and says to return "unknown" when the call did not make it clear.
10. Give it a number, as the design's number plan says. List numbers with
   `listPhoneNumbers` and show each one with the agent it serves now
   (`active_bot_id` is that agent's id, or false; name it from `listAgents`). Attach only the number the user names, with
   `phoneNumberAgentActions` { action: "attach", phone_number_id, agent_id }. If that number serves
   another agent, say that agent stops answering on it, and attach only after
   the user's yes. If no number exists, ask the user whether to buy one or
   import one they own. To buy: ask for the region and for landline or mobile,
   take the `carrier` from the `omnidim://reference/carriers` resource, run
   `searchPhoneNumbers` { region, carrier }, and confirm the exact number and
   price before `purchasePhoneNumber`, which charges the account. To import:
   importTwilioNumber / importExotelNumber / importSipTrunk.
11. If `getAgent` showed `can_publish: true`, save this as version "V1" with `createAgentVersion`. A 409 `no_changes` means a saved version already holds this state: rename that newest version to "V1" with `agentVersionActions` (`action: "rename"`).
12. If the user gave a test number, call it. Otherwise ask the user whether to call their phone now to test the agent. With their number, place the call with `dispatchCall`. Pass `call_context` with a value for every [variable] the welcome and prompt use, and the number from step 10 as `from_number_id` (omit it only if the account has no numbers). A **book** agent writes a real booking on the test call: tell the user before the call, so they can cancel it after.
13. Check `listCallLogs` { agentid, pagesize: 1 } at most 5 times, 30 seconds apart; if no new row appears, tell the user and stop. Then `getCallLog` on its id. The call is verified ONLY if `call_conversation` is non-empty (the agent actually spoke). A successful dispatch response alone is not proof. Tell the user what happened on the call and propose fixes with the `update_agent` playbook.

Final reply, only this: the agent's name and id, the version saved, the settings applied, the conflicts and which source lost, the [MISSING] items, missing tools and open risks, anything the user must set in the dashboard, and six lines to say on the first test call: the happy path, one-word replies, the hardest case for the kind (**persuade**: the toughest objection; **book**: a time with no free slot; **answer**: a question the facts do not cover; **survey**: stopping halfway), a language switch, "are you AI?", and "stop calling". Do not paste the full prompt unless asked.

Throughout: phone numbers are E.164 with a leading `+`. See the `omnidim://guide/routing` resource for the full gotcha list.
