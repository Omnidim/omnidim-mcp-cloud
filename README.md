# omnidim-mcp-cloud

[![Release](https://img.shields.io/github/v/release/Omnidim/omnidim-mcp-cloud)](https://github.com/Omnidim/omnidim-mcp-cloud/releases)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue)](./LICENSE)
[![OmniDimension MCP connector on Glama](https://glama.ai/mcp/connectors/io.github.Omnidim/omnidim-mcp-server/badges/score.svg)](https://glama.ai/mcp/connectors/io.github.Omnidim/omnidim-mcp-server)

The hosted [Model Context Protocol](https://modelcontextprotocol.io) server for [OmniDimension](https://omnidim.io), at `https://mcp.omnidim.io/mcp`. Connect Claude, ChatGPT, Cursor or any MCP client to build and deploy voice AI agents, make calls, and run call campaigns, workflows and WhatsApp in your account.

You sign in with your OmniDimension account in the browser, so you need no API key.

## Connect

[![Install in Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=omnidim&config=eyJ1cmwiOiJodHRwczovL21jcC5vbW5pZGltLmlvL21jcCJ9)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_omnidim-0098FF?logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=omnidim&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fmcp.omnidim.io%2Fmcp%22%7D)

Claude Code, with the server and the [OmniDimension skills](https://github.com/Omnidim/skills) in one step:

```bash
claude plugin install omnidim --marketplace Omnidim/skills
```

Codex:

```bash
codex mcp add omnidim --url https://mcp.omnidim.io/mcp
```

| Client | Setup |
|---|---|
| Claude Desktop, Claude.ai | Settings, Connectors, Add custom connector, then paste `https://mcp.omnidim.io/mcp`. [Claude guide](https://docs.omnidim.io/docs/mcp/connect/claude-desktop) |
| ChatGPT | Add `https://mcp.omnidim.io/mcp` as a custom connector. [MCP overview](https://docs.omnidim.io/docs/mcp) |
| Claude Code | Run the command above, then `/mcp` to sign in. [Claude Code guide](https://docs.omnidim.io/docs/mcp/connect/claude-code) |
| Codex | Run the command above, then `codex mcp login omnidim`. [Codex guide](https://docs.omnidim.io/docs/mcp/connect/codex) |
| Cursor | The button above, or the [Cursor guide](https://docs.omnidim.io/docs/mcp/connect/cursor) |
| VS Code | The button above, or the [VS Code guide](https://docs.omnidim.io/docs/mcp/connect/vscode) |
| Windsurf | [Windsurf guide](https://docs.omnidim.io/docs/mcp/connect/windsurf) |
| Any other MCP client | Add `https://mcp.omnidim.io/mcp` as a remote server |

To give an agent read access only, connect `https://mcp.omnidim.io/mcp/readonly` instead. It lists only the tools that read data (agents, call logs, campaigns, numbers) and refuses any tool that changes data or places a call.

On the first tool call, your client opens the OmniDimension sign-in in your browser. Approve it, and the client stores its own token. To revoke access, remove the connector in your client or at [omnidim.io/api-management](https://omnidim.io/api-management).

Want a local server that runs with an API key instead? Use [`@omnidim-ai/mcp-server`](https://github.com/Omnidim/omnidim-mcp-server). It has the same tools.

## Try these prompts

- "What agents do I have, and which phone numbers are attached to them?"
- "Build a receptionist agent for a dental clinic that books appointments, then give it a phone number."
- "Call +15550100 with my receptionist agent and show me the transcript when the call ends."
- "Start a campaign that calls the contacts in this CSV, 5 calls at a time, between 10 AM and 6 PM."
- "After each call, sort it into booked, callback or not interested, and post the booked ones to Slack."
- "Which calls failed yesterday, and why?"

The server also ships prompts for common jobs (`provision_agent`, `build_outbound_campaign`, `build_workflow`, `audit_calls`, `restore_agent_version`, `book_demo`) and guide resources under `omnidim://guide/` and `omnidim://reference/`.

## Tools

Your client asks you to confirm before a tool that places a call, sends a message, spends money or deletes something.

| Area | What your agent can do | Tools |
|---|---|---|
| Agents | Build, edit and version voice agents, and set what happens after each call | 13 |
| Calls | Place a call and read call logs and transcripts | 3 |
| Call campaigns | Create, start, pace and retry bulk call campaigns | 15 |
| Phone numbers | Search, buy, attach and import numbers (Twilio, Exotel, SIP) | 9 |
| Workflows | Build, test and publish post-call workflows | 4 |
| Knowledge base | Upload files and attach them to agents | 4 |
| Voices and providers | Pick voices, models and providers, and manage cloned voices | 8 |
| Integrations | Connect agents to your APIs and apps | 4 |
| WhatsApp | Numbers, templates, conversations and campaigns | 23 |
| Docs | Search and read [docs.omnidim.io](https://docs.omnidim.io) and the step-by-step playbooks, with no access to your account | 3 |
| Account and demo | Check your balance, start a web call session and book a demo | 5 |

<details>
<summary>All tool names</summary>

| Group | Tools |
|---|---|
| Agents | `listAgents`, `createAgent`, `getAgent`, `updateAgent`, `deleteAgent`, `listPostCallActions`, `addPostCallAction`, `deletePostCallAction`, `updatePostCallAction`, `listAgentVersions`, `createAgentVersion`, `diffAgentVersion`, `agentVersionActions` |
| Calls | `dispatchCall`, `listCallLogs`, `getCallLog` |
| Bulk calls | `fetchBulkCalls`, `createBulkCall`, `addBulkCallContact`, `getBulkCall`, `bulkCallActions`, `listBulkCallLines`, `listBulkCallNumbers`, `addBulkCallNumber`, `setBulkCallNumberActive`, `addBulkCallContacts`, `setBulkCallConcurrency`, `setBulkCallRotation`, `retryBulkCall`, `setBulkCallDailyTimeControl`, `getBulkCallLiveStatus` |
| Phone numbers | `listPhoneNumbers`, `searchPhoneNumbers`, `purchasePhoneNumber`, `releasePhoneNumber`, `setPhoneNumberAutoRenew`, `phoneNumberAgentActions`, `importTwilioNumber`, `importExotelNumber`, `importSipTrunk` |
| WhatsApp | `listWhatsappNumbers`, `importWhatsappNumbers`, `previewWhatsappNumbers`, `getWhatsappNumber`, `listWhatsappTemplates`, `syncWhatsappTemplates`, `getWhatsappCalling`, `setWhatsappCalling`, `listWhatsappConversations`, `getWhatsappConversation`, `whatsappConversationActions`, `listWhatsappMessages`, `sendWhatsappMessage`, `getWhatsappMessage`, `listWhatsappOptOuts`, `addWhatsappOptOut`, `liftWhatsappOptOut`, `listWhatsappCampaigns`, `createWhatsappCampaign`, `getWhatsappCampaign`, `listWhatsappCampaignContacts`, `addWhatsappCampaignContacts`, `whatsappCampaignActions` |
| Knowledge base | `listKnowledgeBaseFiles`, `uploadKnowledgeBaseFile`, `agentKnowledgeBaseActions`, `deleteKnowledgeBaseFile` |
| Workflows | `workflow`, `workflowActions`, `deleteWorkflow`, `showWorkflow` |
| Voice cloning | `listClonedVoices`, `getClonedVoice`, `deleteClonedVoice`, `updateClonedVoice`, `regenerateClonedVoiceSample` |
| Integrations | `listIntegrations`, `createCustomApiIntegration`, `listAgentIntegrations`, `agentIntegrationActions` |
| Providers | `listProviders`, `listVoices`, `getVoice` |
| Account | `getAccountBalance` |
| Sessions | `createSession` |
| Demo | `getDemoQuestions`, `requestDemo`, `bookDemo` |
| Docs | `searchDocs`, `readDoc`, `readGuide` |

</details>

## Build your own client

The server speaks the standard MCP authorization flow ([OAuth 2.1](https://oauth.net/2.1/) with PKCE and Dynamic Client Registration). Clients discover it at `https://mcp.omnidim.io/.well-known/oauth-authorization-server`.

1. Register your client:

   ```bash
   curl -s -X POST https://mcp.omnidim.io/register -H 'content-type: application/json' -d '{"redirect_uris":["https://your-app.example/cb"],"client_name":"My App"}'
   ```

   The response holds your `client_id`.
2. Send the user through the authorization flow, then exchange the code for an access token.
3. Send JSON-RPC requests to `POST https://mcp.omnidim.io/mcp` with `Authorization: Bearer <access_token>`.

## Privacy

What the server stores and how to disconnect: [MCP privacy](https://docs.omnidim.io/docs/mcp/privacy).

## Troubleshooting

| What you see | What to do |
|---|---|
| The sign-in page does not open | In Claude Code, run `/mcp`, pick `omnidim` and choose Authenticate. In other clients, remove the connector and add it again. |
| Tools stopped working after you removed access at omnidim.io | Remove the connector in your client and add it again to sign in. |
| A tool says the read-only endpoint does not run it | You connected `https://mcp.omnidim.io/mcp/readonly`. Connect `https://mcp.omnidim.io/mcp` to change data or place calls. |
| Every tool fails | Check [status.omnidim.io](https://status.omnidim.io), or run `curl https://mcp.omnidim.io/readyz`. A healthy server answers `{"status":"ok"}`. |

## Reporting issues

Open an issue in this repo. Say which client you use, the time it happened, and the tool name. To report a security vulnerability, see [SECURITY.md](./SECURITY.md).

## License

[Apache 2.0](./LICENSE)
