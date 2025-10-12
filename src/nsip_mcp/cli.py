"""Command-line interface for NSIP MCP Server.

This module provides the CLI entry point for starting the MCP server with
configurable transport mechanisms.
"""

import sys

from nsip_mcp.server import start_server


def main() -> None:
    """Main CLI entry point for nsip-mcp-server command.

    Starts the NSIP MCP server with transport configuration from environment variables:
        - MCP_TRANSPORT: stdio (default), streamable-http, or websocket
        - MCP_PORT: Port number for Streamable HTTP/WebSocket (required for non-stdio)
        - MCP_HOST: Host address to bind to (default: 0.0.0.0)
        - MCP_PATH: Path for HTTP endpoints (default: /mcp)

    The server will run until interrupted (Ctrl+C) or an error occurs.

    Exit codes:
        0: Clean shutdown
        1: Configuration or runtime error
    """
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
