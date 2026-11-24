---
name: omnidim-connect
description: "Connect an AI agent to an OmniDimension account through MCP, with the hosted server or a local one. Use when the OmniDimension tools are missing, a tool call fails with 401, or the user asks how to set OmniDimension up."
---

# Connect to OmniDimension

1. Hosted server, signs in with OAuth in the browser:
   - Claude Code: `claude plugin install omnidim --marketplace Omnidim/skills` adds the server and these skills. Then run `/mcp` to sign in. If your Claude Code does not know `--marketplace`, run `claude plugin marketplace add Omnidim/skills`, then `claude plugin install omnidim@omnidim`.
   - Claude.ai, ChatGPT, Cursor and other clients: add `https://mcp.omnidim.io/mcp` as a custom connector.
   - For read access only, use `https://mcp.omnidim.io/mcp/readonly`.
2. Local server, uses an API key from https://omnidim.io/api-management:
   `npx -y @omnidim-ai/mcp-server setup` writes the key and the client config.
3. Check the connection with `getAccountBalance`. A 401 means the key or sign-in expired: sign in again or make a new key.

Guides for each client: https://docs.omnidim.io/docs/mcp. Call `searchDocs` for anything else.
