# nsip-mcp-server

MCP (Model Context Protocol) server for NSIP sheep breeding data. Provides context-efficient API-to-MCP gateway for LLM integrations.

## Installation

```bash
pip install nsip-mcp-server
```

## Quick Start

```bash
# Run with stdio transport (default, for Claude Desktop)
nsip-mcp-server

# Run with HTTP transport
MCP_TRANSPORT=streamable-http MCP_PORT=8000 nsip-mcp-server

# Run with WebSocket transport
MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server
```

## Features

- **15 MCP Tools**: 10 NSIP API tools + 5 Shepherd consultation tools
- **MCP Resources**: URI-based access via `nsip://` scheme
- **MCP Prompts**: Structured workflows for breeding analysis
- **Caching**: TTL-based caching with 1hr expiry
- **Token Management**: Optional summarization for large responses

## Documentation

Full documentation is available at the [project repository](https://github.com/epicpast/nsip-api-client).

## License

MIT License - see [LICENSE](https://github.com/epicpast/nsip-api-client/blob/main/LICENSE) for details.
