---
name: "Agent version history"
description: "How to save, diff, and restore agent config snapshots: which tool to call, what the diff `against` modes mean, how to decide on a restore, and the 403/409 gotchas."
---

# Agent version history

A **version** is a frozen snapshot of an agent's configuration at a point in
time. Use it to save a known-good setup before a risky change, and to roll back
if a change makes the agent worse.

## The tools

- `listAgentVersions` { agent_id } - the timeline, newest first. Each entry has a
  `version_number`, a `kind`, who saved it, and a `change_summary` (an object
  with `first`, true only for the agent's first version, a `count`, and `items`, the
  changes as label, old, new).
- `createAgentVersion` { agent_id, name, note? } - save the agent's CURRENT
  config as a named version.
- `diffAgentVersion` { agent_id, version_number, against? } - what changed (below).
- `restoreAgentVersion` { agent_id, version_number } - write a version back onto
  the agent. On a published agent it writes the draft: callers hear it after
  the user publishes in the dashboard.
- `renameAgentVersion` / `deleteAgentVersion` - tidy the timeline.

`kind` is `manual` (someone saved it) or `system` (a safety backup taken right
before a restore). Nothing saves versions automatically.

## When to snapshot

Call `createAgentVersion` right BEFORE a change you might want to undo (swapping
the model/voice, rewriting the prompt, changing transfer rules). Give it a clear
`name`. The platform does not save versions on its own, so a change you did not
snapshot first cannot be undone.

## How to read a diff

`diffAgentVersion` returns `{ changed, groups }`, each group an area (Settings,
Prompt, Transfer rules, Post-call actions, Knowledge, Integrations, Web widget,
Conversation flow, Other settings) with the specific old -> new changes. Pick the
comparison with `against`:

- **omit / `against=previous`** (default): what changed IN this version vs the
  one before it. Matches the `change_summary` in the list.
- **`against=current`**: what restoring this version would change. `old` is
  this version's value and `new` is the agent's value now: restoring turns
  each `new` back into `old`. Read this before a restore to preview the effect.
- **`against=<number>`**: compare with a specific other version.

## How to decide and perform a restore

1. `listAgentVersions` and scan `change_summary` to find the target version.
2. `diffAgentVersion` { version_number, against: "current" } to preview exactly
   what restoring changes. If nothing meaningful changed, there is nothing to do.
   Show the user the preview, and restore only on their yes.
3. `restoreAgentVersion` { agent_id, version_number }. This first keeps the
   current state as a backup (a new `system` "Backup before restore" version, or
   an existing version that already holds the same state), so the restore is
   itself undoable, then writes the chosen config back. The response's `skipped`
   list reports what was dropped rather than failing the restore (such as
   knowledge files, integrations, languages, the voice or post-call links).
   Report every item in it to the user.
4. Tell the user which version holds the backup; `safety_version` in the restore response names it.

## Gotchas

- Version history is enabled per organization and per plan. If it is off, these
  endpoints return 403 `feature_disabled`, or `feature_not_entitled` when the
  plan does not include it. `getAgent` shows `can_publish: false` in both cases.
- `createAgentVersion` refuses a no-op: if nothing changed since the latest
  version it returns 409 (`no_changes`). The newest version already holds this
  state: use its `version_number`.
- There is a per-agent cap on versions created through the API; at the cap
  `createAgentVersion` returns 409 (`version_limit_reached`). Ask the user which
  old version to delete. The published version cannot be deleted (409
  `version_published`).
- `listAgentVersions` and `diffAgentVersion` are read-only and safe to call
  freely. Restore and delete change the agent and its history: get the user's
  yes first.
