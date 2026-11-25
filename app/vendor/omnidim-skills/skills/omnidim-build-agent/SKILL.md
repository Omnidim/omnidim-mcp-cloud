---
name: omnidim-build-agent
description: "Design, build, test and change an OmniDimension voice agent: ask about the gaps and get the call script approved, build the full prompt and settings, give it a number, test it with a real call, apply fixes safely, and roll back if a change broke it. Use when the user wants a new voice agent, a bot for calls, to fix or change an agent, or to undo agent changes."
---

# Build an OmniDimension voice agent

If the OmniDimension tools are missing, connect the server: https://docs.omnidim.io/docs/mcp. If a field, error or feature is unclear, call `searchDocs` before guessing.

Read the playbook for the task and follow its steps in order. Fill each placeholder in quotes, parentheses or angle brackets from the user's request. Where a playbook names a playbook in the table below, open its file. Where it names any other playbook or an `omnidim://` guide, read it with the `readGuide` tool.

| Task | Playbook | Name |
|---|---|---|
| Design a new agent's calls and get the script approved | [design-agent.md](design-agent.md) | `design_agent` |
| Build the agent from the approved design and test it with a call | [provision-agent.md](provision-agent.md) | `provision_agent` |
| Change or fix an existing agent | [update-agent.md](update-agent.md) | `update_agent` |
| Roll an agent back to an earlier version | [restore-agent-version.md](restore-agent-version.md) | `restore_agent_version` |
