"""
NSIP MCP Server - Context-Efficient API-to-MCP Gateway

This package provides an MCP (Model Context Protocol) server that exposes
NSIP sheep breeding data API capabilities to LLM applications in a
context-efficient manner.

Key Features:
- 9 MCP tools wrapping NSIPClient methods
- Automatic response summarization for large payloads (>2000 tokens)
- In-memory caching with 1-hour TTL
- Multiple transport support (stdio, HTTP SSE, WebSocket)
- Context-aware token management using tiktoken (cl100k_base)

Usage:
    Start the MCP server:
    $ nsip-mcp-server

    Or with custom transport:
    $ MCP_TRANSPORT=http-sse MCP_PORT=8000 nsip-mcp-server

For detailed usage, see quickstart.md in the specs/001-create-an-mcp/ directory.
"""

__version__ = "1.0.0"
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
