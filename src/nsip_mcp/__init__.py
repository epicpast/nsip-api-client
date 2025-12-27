"""
NSIP MCP Server - Context-Efficient API-to-MCP Gateway

This package provides an MCP (Model Context Protocol) server that exposes
NSIP sheep breeding data API capabilities to LLM applications in a
context-efficient manner.

Key Features:
- 15 MCP tools (10 NSIP API + 5 Shepherd consultation)
- MCP Resources via nsip:// URI scheme
- MCP Prompts for guided breeding workflows
- Shepherd AI advisor with 4 domains (breeding, health, calendar, economics)
- Automatic response summarization for large payloads (>2000 tokens)
- In-memory caching with 1-hour TTL
- Multi-platform Docker support (amd64, arm64)
- Multiple transport support (stdio, streamable-http, WebSocket)
- Context-aware token management using tiktoken (cl100k_base)

Usage:
    Start the MCP server:
    $ nsip-mcp-server

    Or with custom transport:
    $ MCP_TRANSPORT=streamable-http MCP_PORT=8000 nsip-mcp-server

For detailed documentation, see docs/mcp-resources.md, docs/mcp-prompts.md,
and docs/shepherd-agent.md.
"""

__version__ = "1.4.4"
__author__ = "Allen R"
__all__ = [
    "__version__",
    "__author__",
]

# Public API exports (will be populated as modules are implemented)
# from nsip_mcp.server import FastMCPServer
# from nsip_mcp.tools import (
#     nsip_get_last_update,
#     nsip_list_breeds,
#     nsip_get_statuses,
#     nsip_get_trait_ranges,
#     nsip_search_animals,
#     nsip_get_animal,
#     nsip_get_lineage,
#     nsip_get_progeny,
#     nsip_search_by_lpn,
# )
