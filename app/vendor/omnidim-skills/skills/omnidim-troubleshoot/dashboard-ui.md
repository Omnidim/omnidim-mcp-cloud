---
name: dashboard_ui
arguments:
  - name: problem
    description: "What looks wrong or missing in the dashboard, in the user's words (e.g. 'I can't see the campaigns page', 'the logo is wrong')."
    required: true
---

# Find why a dashboard screen, feature or setting looks wrong or is missing for this account.

Find why the dashboard shows this:

"(the problem in the user's words)"

If a feature or look is set above the user's account, say "your account administrator".

1. Write the problem as one line: which screen, what the user sees, what they expected, since when.
2. Reproduce it from the account's own data: read the same thing with the tools (for example `listAgents`, `getAgent`, `listCallLogs`, `listPhoneNumbers`). If the data is right and only the screen shows it wrong, it is a display problem. If the data is wrong too, use the [troubleshoot.md](troubleshoot.md) playbook instead.
3. Check whether the setting or feature exists with `searchDocs`.
   - It doesn't exist: say so plainly. Don't invent a setting or a menu.
   - It exists but the user can't see it: their role or their account administrator controls which features they see. Tell them to ask their account administrator.
   - It exists and is on, but the screen ignores it: it is the platform's. Hand it to staff with the screen, what the tools show, and the time it was seen.
4. Answer with what you found, the step the user can take, or that you passed it on.

Handing over: where a step says to hand it to staff or pass it on, open a case with `createSupportCase` (or add to the open one with `addCaseMessage`) holding those ids, if those tools are available; otherwise tell the user to contact support with the same ids.
