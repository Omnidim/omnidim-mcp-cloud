---
name: update_agent
arguments:
  - name: change
    description: "Which agent, and what went wrong or what to change. Add a call id or transcript lines if there are any."
    required: true
---

# Change an agent safely: read what is saved, show the exact edits, back it up, apply on the user's word, and undo if asked.

Update an existing OmniDimension agent:

"(which agent, and what went wrong or what to change)"

1. Fetch the agent with `getAgent`, and the call with `getCallLog` if the user gave a call id. The dashboard may have changed the agent since the last edit, so work from what is saved now. If `published_state.is_published` is true, callers hear version `published_version_number`, not this draft: diagnose calls against that version (`diffAgentVersion` { version_number: <it>, against: "current" }). Tell the user this change edits the draft only, and callers hear it after they publish in the dashboard. If `has_unpublished_changes` is true, say that other draft edits will go live with it.
2. Check these every time and report any mismatch: the voice's gender against the prompt's verb forms; the transcriber and voice language against the primary language; the saved `languages`; the welcome, voicemail, silence nudges and closing line against the identity rule.
3. For each issue, name the cause in one line: a missing rule, a weak rule, two rules that conflict, a wrong fact, a bad example, a setting rather than the prompt, pronunciation, or new content.
4. Pick the size of the fix.
   - SMALL FIX (the default): the least new text. In order of preference: fix an existing example, tighten an existing rule, add one example, add one rule. Never rewrite a section, and never repeat a rule.
   - BIG CHANGE (new facts or stories, a new tone, identity or goal): update every section it touches, keep the eight sections of the `omnidim://guide/agent-prompt` resource, and say "BIG CHANGE" at the top. If the prompt does not use the eight sections, keep its structure, and offer to move it to the eight sections as a separate change.
   Either way, keep the prompt's style. When a fact changes, change every place it appears. Never add a fact the user did not give. Never apply anything that makes the agent deny being AI, threaten, or ignore a stop request: tell the user instead.
5. Show the user:
   - EDITS: # | section | Replace, Insert after or Delete | the exact current text | the exact new text | why. For a BIG CHANGE, show each changed section in full instead.
   - SETTINGS, only if needed: setting | now | change to.
   - WATCH OUT: any other line that could still cause the old behaviour.
   - TEST: two caller lines that would show the fix works.
6. Wait. When the user says "Apply":
   - Backup. If `getAgent` showed `can_publish: false`, version history is off for this agent: tell the user the change cannot be undone, and apply only after they agree. Otherwise save a backup with `createAgentVersion` and keep the `version_number` it returns. A 409 `no_changes` means the newest version already holds this state: take its `version_number` from `listAgentVersions`. A 409 `version_limit_reached` means there is no room for a backup: stop, and ask the user which old version to delete. A 403 `feature_disabled` or `feature_not_entitled` means no history: ask as above. Never apply without a backup `version_number` or the user's yes.
   - Apply exactly these edits with `updateAgent`, sending only the fields you change, in the shape the `omnidim://reference/agent-config` resource gives for reading an agent back. `getAgent` names differ: sections come back as `context_title` and `context_body`, but `updateAgent` takes `title`, `body` and `is_enabled`, and sending the `getAgent` names back does not save the sections. Copy `is_enabled` for every section, or a disabled section turns back on. Send the complete `context_breakdown` list, never only the changed section, because it replaces the whole list. In `end_call`, send `enabled` only to turn ending the call on or off. If the response has `warnings`, part of the edit was not saved: fix each named field and send it again.
   - Fetch the agent again and check that every section has its title and body. If any is blank, restore the backup `version_number` at once and tell the user.
   - Save the new version (V1.1, V1.2 and so on) with `createAgentVersion`, and confirm in one line what changed.
   If the user says "Undo", restore the backup `version_number` with `agentVersionActions` (`action: "restore"`).
7. Offer a test call to check the fix, as in the `provision_agent` playbook's test steps. On a published agent, wait until the user has published: a call before that plays the old version.
