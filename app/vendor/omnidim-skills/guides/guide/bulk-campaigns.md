---
name: "Running outbound campaigns"
description: "The campaign lifecycle end to end: draft, batch contacts (two contact shapes, do not mix), rotation, concurrency arithmetic, the agent-timezone trap, cursor-paged results."
---

# Running outbound campaigns

## Normal or dynamic
- One-time list: a normal campaign. Create it as a draft with the first rows in
  `contact_list`, add the rest with `addBulkCallContacts`, then start it after
  the user's go-ahead.
- Continuous leads (form fills, CRM events): a dynamic campaign (`is_dynamic: true`,
  no contact list) fed by `addBulkCallContact` as each lead arrives. The faster a
  fresh lead is called, the higher the conversion. One `addBulkCallContact`
  starts a draft campaign at once, so send it only after the user approves the
  launch.

## The two contact shapes (do not mix them)
- `createBulkCall`'s `contact_list` rows are FLAT:
  `{ "phone_number": "+1...", "any_other_key": "reaches the agent as context" }`.
- `addBulkCallContact` / `addBulkCallContacts` instead take
  `{ to_number, custom_variables: {...}, metadata: {...} }`. `metadata` is
  bookkeeping the agent never sees.
- Sending `custom_variables` inside a `contact_list` row does not error; it becomes
  one nested variable and garbles the agent's context.

## Build as a draft, then start
- `createBulkCall` { name, phone_number_id, save_as_draft: true, contact_list, ... }.
  A normal campaign needs `contact_list` at create; only a dynamic one may leave
  it out. Keep the returned `id`. Without `save_as_draft` the campaign dials the
  moment it is created.
- `addBulkCallContacts` accepts up to 1000 contacts per request. Invalid rows come
  back in `rejected` with their index and reason; valid rows are still added, so one
  bad number never costs the batch.
- `bulkCallActions` with `action: "start"` launches a draft.
- Adding contacts is NOT dynamic-only: any campaign that is not cancelled or failed
  accepts them, and a completed campaign wakes up and dials again.

## Size concurrency with arithmetic, not vibes
- Calls per hour per channel = 3600 / average call seconds (~40/hour at 90s).
- Channels needed = target calls per hour / per-channel rate.
- Example: 100,000 calls in an 8-hour day is 12,500/hour, ~315 channels. The failure
  mode: concurrency 5 against 10,000 leads is ~200 calls/hour, a 50-hour "today"
  campaign.
- `setBulkCallConcurrency` changes it mid-run. A value above the org's ceiling is
  refused.

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
  local date and time it works with during calls. Suggest the customers' region,
  and change it only after the user's yes: the agent may serve other calls.

## Watching a campaign and reading results
- `getBulkCallLiveStatus` for progress counts while it runs, when the user asks.
  Do not poll it in a loop.
- `listBulkCallLines` for per-contact outcomes: `pagesize` 10 (each row is about
  2 KB, and a bigger page is cut to fit), filtered by `call_status` where it
  helps. Follow `next_cursor` until it comes back null, never build a cursor
  yourself. After 10 pages, ask the user before reading more.
  `include_total` once for a header, not on every page.
- Rows carry `recording_id`, not the transcript; `getCallLog` serves it.
- `retryBulkCall` re-queues contacts that did not connect; it refuses a campaign
  that is still running.

## Contact rules
- Numbers are E.164 with the country code. Run one campaign per country code.
- Dashboard CSV uploads need the phone column named exactly `phone_number`.
