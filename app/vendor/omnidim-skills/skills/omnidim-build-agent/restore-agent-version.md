# Safely roll an agent back to an earlier saved version: find the right snapshot, preview exactly what restoring changes, then restore.

Roll agent <agent_id> back to an earlier version.

Goal: "(describe which earlier state you want back)"

Follow these steps in order. Do NOT restore blindly, preview first.
1. `listAgentVersions` { agent_id: <agent_id> }. Versions come newest first; each has a `version_number`, `kind` (manual or system), who saved it, when, and a `change_summary` (what changed in that version). Use the names, timestamps, and change summaries to find the one that matches the goal above. If version history is off for this org these calls return 403 (feature_disabled); report that and stop. A 403 feature_not_entitled means the plan has no version history.
2. Preview the effect: `diffAgentVersion` { agent_id: <agent_id>, version_number: <chosen>, against: "current" }. This shows what restoring that version would change, grouped by area (Settings, Prompt, Transfer rules, etc.). In each change, `old` is this version's value and `new` is the agent's value now: restoring turns each `new` back into `old`. If it reports no meaningful change, tell the user there is nothing to restore and stop. Show the user this preview and restore only on their yes.
3. Restore: `restoreAgentVersion` { agent_id: <agent_id>, version_number: <chosen> }. This automatically keeps the current state as a backup first (a new "Backup before restore" version, or an existing version that already holds the same state), so the restore is itself undoable, then writes the chosen config back. On a published agent it writes the draft only: callers hear it after the user publishes in the dashboard. Report every item in the response's `skipped` list to the user: anything that no longer exists or is not allowed is dropped, not restored.
4. Confirm: tell the user which version holds the backup (`safety_version` in the restore response) and that they can undo by restoring it.

See the `omnidim://guide/agent-versioning` resource for the full tool list and the diff `against` modes.
