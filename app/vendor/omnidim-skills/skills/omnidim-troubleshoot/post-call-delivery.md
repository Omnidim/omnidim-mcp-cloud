---
name: post_call_delivery
arguments:
  - name: destination
    description: "Where results should arrive (e.g. 'Google Sheet', 'my CRM webhook', 'Slack')."
    required: true
  - name: agent_id
    description: "Optional agent id, if the user named the agent."
    required: false
---

# Find why call results stop reaching a Google Sheet, webhook, CRM, Slack, email or other after-call action.

Find why call results don't reach "(where results should arrive)":

1. Find the agent: use the id if given, else `listAgents` once and pick the one the user means.
2. Read its after-call actions with `listPostCallActions` { "agent_id": <id> }. Check the action for that destination exists, points at the right place (spreadsheet and worksheet, webhook URL, channel) and which call statuses trigger it. Failed, busy and no-answer calls trigger nothing unless those statuses are ticked.
3. Read a recent call that should have delivered with `getCallLog` and look at two things:
   - `post_call_actions`: each destination's list holds a delivery for this call with its `status` and `error_message`. An empty list means nothing was sent for this call; an error means it was sent and failed (read the error: a missing Sheets sign-in, a webhook URL that isn't public, a rejected request).
   - `post_call_override`: when `applied` has entries, the call was dialed with its own after-call actions through `__post_call_actions`, and those replaced the agent's own for that call. The agent's Sheet, Slack, CRM and other actions did not run.
4. If results stopped after the user connected another system (a CRM, a script, an automation) and the newer calls have `post_call_override` while older ones don't, that system dials with its own actions. A call dialed this way can carry only an email and a webhook, never a Sheet. The fix: stop sending `__post_call_actions` from that system, and add its webhook to the agent's own after-call actions next to the existing destination, so every call reaches both.
5. Compare one call that delivered with one that didn't, following the [troubleshoot.md](troubleshoot.md) playbook from its step 4, and answer with both call ids, the cause, the fix steps and one test call to confirm.
