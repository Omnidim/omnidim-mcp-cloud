# omnidim-mcp-cloud

Hosted Model Context Protocol server for [OmniDimension](https://omnidim.io). Connect Claude, ChatGPT, or any MCP-compatible client to your OmniDimension account.

## Connect

Add this URL as a custom MCP server in your client:

```
https://mcp.omnidim.io/mcp
```

The service speaks the standard MCP authorization flow ([OAuth 2.1](https://oauth.net/2.1/) + PKCE + Dynamic Client Registration), so clients pick up the rest from discovery at `https://mcp.omnidim.io/.well-known/oauth-authorization-server`.

### Claude Code

```bash
claude mcp add --transport http omnidim https://mcp.omnidim.io/mcp --scope user
```

Then run `/mcp` inside Claude Code and approve the consent screen in the browser.

### Claude Desktop, Claude.ai, and other clients

Open your client's MCP / connector settings, add a custom server, and paste `https://mcp.omnidim.io/mcp`. Per-client setup guides at [docs.omnidim.io](https://docs.omnidim.io).

### Programmatic clients

```bash
curl -s -X POST https://mcp.omnidim.io/register \
  -H 'content-type: application/json' \
  -d '{"redirect_uris":["https://your-app.example/cb"],"client_name":"My App"}'
```

Returns a `client_id`. After the user approves consent in the browser and you exchange the authorization code for a token, send JSON-RPC `tools/call` requests to `POST /mcp` with `Authorization: Bearer <access_token>`.

Looking for the local stdio variant for your IDE? Use [`@omnidim-ai/mcp-server`](https://github.com/Omnidim/omnidim-mcp-server) instead.

## Security

To report a security vulnerability, please see [SECURITY.md](./SECURITY.md).

## License

[Apache 2.0](./LICENSE)
