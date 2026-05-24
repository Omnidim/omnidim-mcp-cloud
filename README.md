# omnidim-mcp-cloud

Hosted Model Context Protocol server for [OmniDimension](https://omnidim.io). Connect Claude, ChatGPT, or any MCP-compatible client to your OmniDimension account.

## Connect

The service speaks the standard MCP authorization flow ([OAuth 2.1](https://oauth.net/2.1/) + PKCE + Dynamic Client Registration). Most MCP clients can pick it up from the discovery URL:

```
https://mcp.omnidim.io/.well-known/oauth-authorization-server
```

For clients that need a manual URL, point them at:

```
https://mcp.omnidim.io
```

## Quick example

```bash
# Register a client
CID=$(curl -s -X POST https://mcp.omnidim.io/register \
  -H 'content-type: application/json' \
  -d '{"redirect_uris":["https://your-app.example/cb"],"client_name":"My App"}' \
  | jq -r .client_id)

# After the user approves consent in their browser and you exchange the
# code for a token, drive MCP tools as usual.
```

Full reference at [docs.omnidim.io](https://docs.omnidim.io).

Looking for the local stdio variant for your IDE? Use [`@omnidim-ai/mcp-server`](https://github.com/Omnidim/omnidim-mcp-server) instead.

## Security

To report a security vulnerability, please see [SECURITY.md](./SECURITY.md).

## License

[Apache 2.0](./LICENSE)
