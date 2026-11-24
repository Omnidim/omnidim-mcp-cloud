# Set up and launch a bulk-call campaign safely: draft it, batch the contacts in, size concurrency from the numbers, check calling hours, then start and watch it.

Set up and launch an OmniDimension bulk-call campaign for this goal:

"(describe who to call and why)"

Follow these steps in order. Write tools take flat top-level arguments (no `requestBody` wrapper).
A campaign dials real people and spends real money: confirm the plan with the user before
`startBulkCall`, and never start one they have not approved.

1. Decide the shape: a one-time list is a normal campaign; continuously arriving leads mean a
   dynamic campaign (`is_dynamic: true`, no `contact_list`) fed by `addBulkCallContact` instead of
   step 5. While a campaign is a draft, add contacts only with `addBulkCallContacts`: one
   `addBulkCallContact` starts a draft campaign at once, so use it only after step 8's go-ahead.
2. Number and agent: If the user named a dialing number, use its phone_number_id. Otherwise call `listPhoneNumbers` and pick the dialing number WITH the user; never pick silently. If the user named an agent, pass its id as `bot_id` so it runs the calls even if the number has a different or no agent attached. Otherwise, if the number has an agent attached it runs the calls; if not, pass a `bot_id`.
3. Create it as a draft with `createBulkCall`
   { name, phone_number_id, save_as_draft: true, concurrent_call_limit: <sized below>,
     contact_list: [{ "phone_number": "+1...", ... }] }.
   A normal campaign needs its first rows in `contact_list` (flat shape); add the rest in step 5.
   Add `rotation` when dialing from several numbers (see the bulk-campaigns resource for the
   shape). Keep the returned `id`.
4. Size concurrency from the goal's numbers, not a guess: per channel, 3600 / average call seconds
   gives calls per hour (~40 at 90s); divide the target hourly rate by that. Show the arithmetic
   to the user.
5. Add the remaining contacts with `addBulkCallContacts` in batches of up to 1000:
   { campaign_id, contacts: [{ to_number: "+1...", custom_variables: {...} }] }.
   This shape differs from create's contact_list on purpose; do not mix them. Report anything
   that comes back in `rejected` with its row index. Each `custom_variables` key fills the
   matching [placeholder] in the agent's greeting and prompt, so every row needs every key the
   agent uses, or the agent skips the placeholder and the line sounds broken.
6. Calling hours: ask the user for the calling hours and the customers' timezone. If they want
   none, say the campaign dials around the clock. Set the window with `setBulkCallDailyTimeControl`
   (both the stop and start blocks are required) and pass `daily_stop_timezone`/
   `daily_start_timezone` for the customers' region; left out they fall back to the campaign's
   timezone, and a mismatch dials people at night. Suggest setting the agent's own `timezone`
   field to the customers' region too. Change it with `updateAgent` only after the user's yes:
   the agent may serve other calls.
7. Check the agent's greeting against the `omnidim://guide/call-tips` resource (a name check of
   8 words or fewer loses far fewer calls in the first seconds). Suggest changes; never edit the
   agent without the user's yes.
8. Show the user the plan (campaign id, contact count, concurrency, window, rotation) and get
   their explicit go-ahead. Then `startBulkCall`.
9. Watch it: `getBulkCallLiveStatus` for progress when the user asks; do not poll it in a loop.
   When it finishes, read per-contact outcomes
   with `listBulkCallLines` (`pagesize` 10, since each row is about 2 KB and a bigger page is cut;
   filter by `call_status`; follow `next_cursor` for at most 10 pages, then ask the user before
   reading more) and offer `retryBulkCall` for
   contacts that did not connect.

See the `omnidim://guide/bulk-campaigns` resource for the full rules and failure modes.
