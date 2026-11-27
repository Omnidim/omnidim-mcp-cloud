---
name: calls_not_working
arguments:
  - name: problem
    description: "What fails, in the user's words (e.g. 'my number stopped taking calls this morning')."
    required: true
  - name: phone_number
    description: "Optional number the problem is on, in E.164 with a leading +."
    required: false
---

# Find why calls on a number don't connect, don't ring, drop, or never reach the agent.

Find why calls fail here, from the account's own data:

"(the problem in the user's words)"

1. Write the problem as one line: inbound or outbound, which number, since when, and what happens (no ring, busy, drops at once, connects but the agent is silent). If the agent speaks but sounds or behaves wrong, use the `call_audio_behavior` playbook ([call-audio-behavior.md](call-audio-behavior.md)) instead.
2. Read the number with `listPhoneNumbers` and find it by its number. Note `id`, `number_provider`, `carrier_label`, `expiry_date` and `active_bot_id`.
   - Not in the list: the number was released or belongs to another account. Use the `billing` playbook ([billing.md](billing.md)) for a released number.
   - `expiry_date` in the past: the number's paid period ended. That is the answer.
   - Inbound and `active_bot_id` empty: no agent answers this number. The fix is to attach the agent to the number.
3. If an agent is attached, read it with `getAgent` { "agent_id": <active_bot_id> }. Check it is the agent the user means. If `published_state.is_published` is true, callers hear the published version, not the latest draft.
4. Read the balance with `getAccountBalance`. A balance at or below zero stops calls unless `plan.is_usage_based` is true. A `403` means the user lacks Billing access: skip this step and say so.
5. List the number's recent calls with `listCallLogs` { "to_number": "<number>" for inbound or "from_number": "<number>" for outbound, "call_direction": "inbound" | "outbound", "date_from": "<day before it broke>", "date_to": "<today>", "include_details": false, "pagesize": 5 }.
   - No calls since the break, inbound: the calls never reached the platform. The cause is on the number or carrier side, or callers dial another number. Go to step 6.
   - Calls exist: read `call_status` and `hangup_reason` on the bad ones, then `getCallEvents` { "call_log_id": <id> } on one of them for `end_reason`, `answered_by`, `amd_detected` and whether the agent spoke at all. Compare one good call before the break with one bad call after it with `getCallLog`, following the [troubleshoot.md](troubleshoot.md) playbook from its step 4.
   - Outbound calls accepted but never connected: the number may not reach the destination country. A `dispatchCall` that returns `success: true` only means the request was accepted.
6. Check the account's other numbers with the same `carrier_label` from step 2, with `listCallLogs` the same way.
   - They fail since the same time too: the cause is on that carrier lane, not this number. This is the platform's or carrier's to fix: hand it to staff with the number ids and call ids.
   - They work: the cause is this one number. Hand it to staff with the number id, the last good call id and the first bad call id, unless steps 2 to 4 already found it.
   - No other number on that carrier: say so and hand it over the same way.
7. Answer with the cause in plain words, the call ids that prove it, and the fix as steps the user can take. Find the exact dashboard steps with `searchDocs`. End with one test: one call to or from the number, then a new row in `listCallLogs`.

Handing over: where a step says to hand it to staff or pass it on, open a case with `createSupportCase` (or add to the open one with `addCaseMessage`) holding those ids, if those tools are available; otherwise tell the user to contact support with the same ids.
