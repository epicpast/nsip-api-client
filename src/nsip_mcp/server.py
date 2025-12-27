"""FastMCP server initialization and configuration.

This module sets up the FastMCP server instance and configures transport mechanisms
for MCP protocol communication.
"""

import sys
import time

from fastmcp import FastMCP

from nsip_mcp.metrics import server_metrics
from nsip_mcp.transport import TransportConfig, TransportType

# Track server startup time
_startup_start = time.time()

# Initialize FastMCP server instance
mcp = FastMCP("NSIP Sheep Breeding Data")

# Import tools to register them with the MCP server
# This ensures all @mcp.tool() decorated functions are loaded
# Import AFTER mcp instance creation to avoid circular import
import nsip_mcp.mcp_tools  # noqa: F401, E402

# Import prompts to register them with the MCP server
# This ensures all @mcp.prompt() decorated functions are loaded
import nsip_mcp.prompts  # noqa: F401, E402

# Import resources to register them with the MCP server
# This ensures all @mcp.resource() decorated functions are loaded
import nsip_mcp.resources  # noqa: F401, E402

# Import shepherd agent for comprehensive husbandry guidance
# This makes the ShepherdAgent available for tool implementations
import nsip_mcp.shepherd  # noqa: F401, E402


def get_transport():
    """Get transport configuration from environment.

    Returns:
        Transport instance based on MCP_TRANSPORT environment variable

    Raises:
        ValueError: If transport configuration is invalid
    """
    config = TransportConfig.from_environment()

    # FastMCP will handle transport setup based on config
    # The actual transport initialization happens in the run() call
    return config


def start_server():
    """Start the MCP server with configured transport.

    This function initializes the server and starts listening for MCP protocol messages.
    The server will run until interrupted (Ctrl+C) or an error occurs.
    """
    transport_config = get_transport()

    # Pre-load knowledge base YAML files to eliminate first-request latency
    from nsip_mcp.knowledge_base.loader import preload_all

    preload_all()

    # Record startup time (SC-007)
    startup_duration = time.time() - _startup_start
    server_metrics.set_startup_time(startup_duration)

    # Log startup information to stderr (stdout reserved for JSON-RPC in stdio mode)
    log = sys.stderr.write
    log(f"Starting NSIP MCP Server with {transport_config.transport_type.value} transport\n")
    log(f"Startup time: {startup_duration:.3f}s (target: <3s)\n")

    # Start server with configured transport
    # FastMCP 2.12.4+ provides native Streamable HTTP support
    if transport_config.transport_type == TransportType.STDIO:
        # stdio uses default stdin/stdout - no banner to stdout (would corrupt JSON-RPC)
        log("Listening on stdin/stdout\n")
        mcp.run(show_banner=False)
    elif transport_config.transport_type == TransportType.STREAMABLE_HTTP:
        # Streamable HTTP (MCP spec 2025-03-26)
        log(
            f"Listening on {transport_config.host}:{transport_config.port}{transport_config.path}\n"
        )
        mcp.run(
            transport="streamable-http",
            host=transport_config.host,
            port=transport_config.port,
            path=transport_config.path,
        )
    elif transport_config.transport_type == TransportType.WEBSOCKET:
        # WebSocket transport
        log(f"Listening on ws://{transport_config.host}:{transport_config.port}/ws\n")
        # FastMCP types don't include websocket transport but it works at runtime
        mcp.run(
            transport="websocket",  # type: ignore[arg-type]
            host=transport_config.host,
            port=transport_config.port,
        )


@mcp.tool()
def get_server_health() -> dict:
    """Get server health status and performance metrics.

    Returns comprehensive server metrics including:
    - Discovery times (SC-001: <5s target)
    - Summarization performance (SC-002: >=70% reduction target)
    - Validation success rate (SC-003: >=95% target)
    - Cache performance (SC-006: >=40% hit rate target)
    - Connection statistics (SC-005: 50+ concurrent target)
    - Startup time (SC-007: <3s target)
    - Success criteria evaluation

    Returns:
        Dict containing all server metrics and success criteria status

    Example:
        >>> health = get_server_health()
        >>> print(health['startup_time_seconds'])
        0.245
        >>> print(health['success_criteria']['SC-001 Discovery <5s'])
        True
    """
    return server_metrics.to_dict()
