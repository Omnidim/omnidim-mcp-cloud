---
name: audit_calls
arguments:
  - name: focus
    description: "What to look into, in plain language (e.g. 'why are calls failing', 'summarize today's calls for agent 123')."
    required: true
  - name: agent_id
    description: "Optional agent id to filter to (the listAgents / createAgent id)."
    required: false
  - name: call_status
    description: "Optional status filter. Note the enum uses a hyphen for no-answer: completed | busy | failed | no-answer."
    required: false
---

# Review and summarize call logs: find failures, inspect transcripts and sentiment, or audit a specific agent or campaign.

Audit OmniDimension call logs for this question:

"(describe what to look into)"

1. List recent calls with `listCallLogs` { "pagesize": 5, "include_details": false }. Add `"agentid"` or `"call_status"` when the user named an agent or a status.
   - Keep `include_details: false` and `pagesize` 5 while you scan. Even short rows are about 2.5 KB, and the response is trimmed past a size cap: a page of 50 short rows comes back as 6. Narrow with filters and `pageno` instead of a bigger page.
   - Filters: `agentid` (note: no underscore) for one agent, `bulk_call_id` for one campaign, `call_status` for triage. The status enum uses a hyphen: completed | busy | failed | no-answer.
   - Each row carries `id`, `call_status`, `sentiment_score` and cost. For one day or a range, add `"date_from"` and `"date_to"` (`YYYY-MM-DD`, in the account's time zone).
2. For each call of interest, call `getCallLog` { call_log_id: <row id> } for the full transcript (`call_conversation`), `interactions`, `extracted_variables`, `recording_url`, and per-turn latency/cost. Note: an empty `call_conversation` means the agent never spoke (a silent call), not that the call is missing.
3. Summarize the answer to "(describe what to look into)": group by status or agent, surface failure reasons and low-sentiment calls, and cite specific `call_log_id`s.

See the `omnidim://guide/routing` resource for the full gotcha list.
