"""FastMCP server initialization and configuration.

This module sets up the FastMCP server instance and configures transport mechanisms
for MCP protocol communication.
"""

import time

from fastmcp import FastMCP

from nsip_mcp.metrics import server_metrics
from nsip_mcp.transport import TransportConfig

# Track server startup time
_startup_start = time.time()

# Initialize FastMCP server instance
mcp = FastMCP("NSIP Sheep Breeding Data")

# Import tools to register them with the MCP server
# This ensures all @mcp.tool() decorated functions are loaded
# Import AFTER mcp instance creation to avoid circular import
import nsip_mcp.mcp_tools  # noqa: F401, E402


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

    # Record startup time (SC-007)
    startup_duration = time.time() - _startup_start
    server_metrics.set_startup_time(startup_duration)

    # Log startup information
    print(f"Starting NSIP MCP Server with {transport_config.transport_type.value} transport")
    print(f"Startup time: {startup_duration:.3f}s (target: <3s)")
    if transport_config.port:
        print(f"Listening on port {transport_config.port}")

    # Start server with configured transport
    # Note: FastMCP's run() method will be called with appropriate transport settings
    # For stdio: mcp.run() uses stdin/stdout by default
    # For HTTP SSE/WebSocket: mcp.run() will need server_transport parameter
    # TODO: Update with actual FastMCP 2.0 transport API when implementing CLI
    mcp.run()


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
