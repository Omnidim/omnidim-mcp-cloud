---
name: troubleshoot
arguments:
  - name: problem
    description: "What is wrong, in the user's words (e.g. 'my sheet stopped filling since yesterday')."
    required: true
---

# Find what changed and prove the cause of a problem in the account, with one good and one bad call.

Find the cause of this problem from the account's own data:

"(the problem in the user's words)"

1. Write the problem as one line: what used to work, what doesn't now, since when. Note every id the user gave (agent, call, campaign, number). "Since yesterday" or "after I did X" means something changed: the job is to find that difference.
2. Check the setting that should make it work first. For an agent, `getAgent` and `listPostCallActions`; for a number, `listPhoneNumbers`; for a campaign, `getBulkCall`. If that setting is missing or wrong, that is the answer: say which setting and what it should be.
3. If the setting is right, compare a good day with a bad day. List the agent's calls for a few days before and after the change with `listCallLogs` { "agentid": <id>, "date_from": "<day>", "date_to": "<day>", "include_details": false }. Look at how the calls were started (`bulk_call_id` set means a campaign; none means a single call from the API, a workflow or the dashboard) and whether `post_call_override` is set.
4. Compare one good call with one bad call. Read both with `getCallLog` and go through them field by field. The field that differs is the lead: how the call was started, `post_call_override`, the delivery lists under `post_call_actions`, `call_status`, `hangup_reason`.
5. Check it isn't a one-off: count how many bad-day calls share that difference and how many good-day calls don't.
6. Decide whose it is: the account's setup (the platform did what its settings say), the platform (the setup is right but the result is wrong), or the carrier or provider. Check the docs with `searchDocs` before calling it a platform fault: documented behavior is not a bug.
   - Some things no tool shows: the carrier's own logs, server logs, and anything said on a phone call or chat outside the account. When the answer depends on one of those, say so plainly and what a teammate would check, instead of guessing.
7. Answer with proof: the cause in plain words, one good call id and one bad call id, and the fix as steps.
   - Only steps the user can really take: a setting, field or action you saw in a tool result or a doc. Never a step the platform doesn't have.
   - Leave out steps that change nothing: if a setting you checked is already right, say it is fine instead of asking them to check or save it again.
   - End with one test that confirms the fix (e.g. "place one call and check a new row appears").
