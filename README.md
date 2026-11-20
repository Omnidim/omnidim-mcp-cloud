# omnidim-mcp-cloud

[![Release](https://img.shields.io/github/v/release/Omnidim/omnidim-mcp-cloud)](https://github.com/Omnidim/omnidim-mcp-cloud/releases)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache_2.0-blue)](./LICENSE)

The hosted [Model Context Protocol](https://modelcontextprotocol.io) server for [OmniDimension](https://omnidim.io), at `https://mcp.omnidim.io/mcp`. Connect Claude, ChatGPT, Cursor or any MCP client, and it can build voice agents, place calls, run campaigns, send WhatsApp messages and read call logs in your account.

You sign in with your OmniDimension account in the browser, so you need no API key.

## Connect

[![Install in Cursor](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/en/install-mcp?name=omnidim&config=eyJ1cmwiOiJodHRwczovL21jcC5vbW5pZGltLmlvL21jcCJ9)
[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_omnidim-0098FF?logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=omnidim&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fmcp.omnidim.io%2Fmcp%22%7D)

| Client | Setup |
|---|---|
| Claude Code | `claude mcp add --transport http omnidim https://mcp.omnidim.io/mcp`, then run `/mcp` and approve in the browser |
| Claude Desktop, Claude.ai | Settings, Connectors, Add custom connector. See the [Claude guide](https://docs.omnidim.io/docs/mcp/connect/claude-desktop) |
| Cursor | Use the button above, or the [Cursor guide](https://docs.omnidim.io/docs/mcp/connect/cursor) |
| VS Code | Use the button above, or the [VS Code guide](https://docs.omnidim.io/docs/mcp/connect/vscode) |
| Windsurf | [Windsurf guide](https://docs.omnidim.io/docs/mcp/connect/windsurf) |
| Codex | [Codex guide](https://docs.omnidim.io/docs/mcp/connect/codex) |
| ChatGPT and other clients | Add `https://mcp.omnidim.io/mcp` as a custom connector. See the [MCP overview](https://docs.omnidim.io/docs/mcp) |

To give an agent read access only, connect `https://mcp.omnidim.io/mcp/readonly` instead. It lists only the tools that read data (agents, call logs, campaigns, numbers) and refuses any tool that changes data or places a call.

On the first tool call, your client opens the OmniDimension sign-in in your browser. Approve it, and the client stores its own token. To revoke access, remove the connector in your client or at [omnidim.io/api-management](https://omnidim.io/api-management).

Want a local server that runs with an API key instead? Use [`@omnidim-ai/mcp-server`](https://github.com/Omnidim/omnidim-mcp-server). It has the same tools.

## Try these prompts

- "What agents do I have, and which phone numbers are attached to them?"
- "Build a receptionist agent for a dental clinic that books appointments, then give it a phone number."
- "Call +15550100 with my receptionist agent and show me the transcript when the call ends."
- "Start a campaign that calls the contacts in this CSV, 5 calls at a time, between 10 AM and 6 PM."
- "Which calls failed yesterday, and why?"

The server also ships prompts for common jobs (`provision_agent`, `build_outbound_campaign`, `build_workflow`, `audit_calls`, `restore_agent_version`, `book_demo`) and guide resources under `omnidim://guide/` and `omnidim://reference/`.

## Tools

Most tools map to one endpoint of the [OmniDimension API](https://docs.omnidim.io). Your client asks you to confirm before a tool that places a call, sends a message, spends money or deletes something.

| Group | Tools |
|---|---|
| Agents | `listAgents`, `createAgent`, `getAgent`, `updateAgent`, `deleteAgent`, `listPostCallActions`, `addPostCallAction`, `deletePostCallAction`, `updatePostCallAction`, `listAgentVersions`, `createAgentVersion`, `deleteAgentVersion`, `renameAgentVersion`, `diffAgentVersion`, `restoreAgentVersion` |
| Calls | `dispatchCall`, `listCallLogs`, `getCallLog` |
| Bulk calls | `fetchBulkCalls`, `createBulkCall`, `addBulkCallContact`, `getBulkCall`, `bulkCallActions`, `cancelBulkCall`, `listBulkCallLines`, `listBulkCallNumbers`, `addBulkCallNumber`, `setBulkCallNumberActive`, `addBulkCallContacts`, `startBulkCall`, `setBulkCallConcurrency`, `setBulkCallRotation`, `retryBulkCall`, `setBulkCallDailyTimeControl`, `getBulkCallLiveStatus` |
| Phone numbers | `listPhoneNumbers`, `searchPhoneNumbers`, `purchasePhoneNumber`, `releasePhoneNumber`, `setPhoneNumberAutoRenew`, `attachPhoneNumber`, `detachPhoneNumber`, `importTwilioNumber`, `importExotelNumber`, `importSipTrunk` |
| WhatsApp | `listWhatsappNumbers`, `importWhatsappNumbers`, `previewWhatsappNumbers`, `getWhatsappNumber`, `listWhatsappTemplates`, `syncWhatsappTemplates`, `getWhatsappCalling`, `setWhatsappCalling`, `listWhatsappConversations`, `getWhatsappConversation`, `takeOverWhatsappConversation`, `handBackWhatsappConversation`, `listWhatsappMessages`, `sendWhatsappMessage`, `getWhatsappMessage`, `listWhatsappOptOuts`, `addWhatsappOptOut`, `liftWhatsappOptOut`, `listWhatsappCampaigns`, `createWhatsappCampaign`, `getWhatsappCampaign`, `listWhatsappCampaignContacts`, `addWhatsappCampaignContacts`, `launchWhatsappCampaign`, `pauseWhatsappCampaign`, `resumeWhatsappCampaign`, `cancelWhatsappCampaign` |
| Knowledge base | `listKnowledgeBaseFiles`, `canUploadFile`, `uploadKnowledgeBaseFile`, `attachKnowledgeBaseFiles`, `detachKnowledgeBaseFiles`, `deleteKnowledgeBaseFile` |
| Workflows | `listWorkflowNodeTypes`, `getWorkflowNodeType`, `listWorkflowFieldOptions`, `listWorkflows`, `createWorkflow`, `getWorkflow`, `deleteWorkflow`, `editWorkflow`, `validateWorkflow`, `publishWorkflow`, `activateWorkflow`, `deactivateWorkflow`, `testWorkflow`, `getWorkflowExecution`, `showWorkflow` |
| Voice cloning | `listClonedVoices`, `getClonedVoice`, `deleteClonedVoice`, `updateClonedVoice`, `getClonedVoiceSample`, `regenerateClonedVoiceSample` |
| Integrations | `listIntegrations`, `createCustomApiIntegration`, `listAgentIntegrations`, `attachAgentIntegration`, `detachAgentIntegration` |
| Providers | `listLLMProviders`, `listVoices`, `listSTTProviders`, `listTTSProviders`, `listAllProviders`, `getVoice` |
| Account | `getAccountBalance` |
| Sessions | `createSession` |
| Demo | `getDemoQuestions`, `requestDemo`, `bookDemo` |

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

## Reporting issues

Open an issue in this repo. To report a security vulnerability, see [SECURITY.md](./SECURITY.md).

## License

[Apache 2.0](./LICENSE)
