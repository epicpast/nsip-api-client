"""Transport configuration for MCP server.

This module handles transport mechanism selection and configuration for the MCP server,
supporting stdio (default), Streamable HTTP, and WebSocket transports.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TransportType(Enum):
    """Supported MCP transport mechanisms."""

    STDIO = "stdio"
    STREAMABLE_HTTP = "streamable-http"
    WEBSOCKET = "websocket"


@dataclass
class TransportConfig:
    """MCP server transport configuration.

    Attributes:
        transport_type: The transport mechanism to use
        port: Port number for Streamable HTTP and WebSocket transports (required for non-stdio)
        host: Host address to bind to (default: 0.0.0.0)
        path: Path for HTTP endpoints (default: /mcp)
    """

    transport_type: TransportType
    port: Optional[int] = None
    host: str = "0.0.0.0"  # nosec B104  # MCP server intentionally binds to all interfaces
    path: str = "/mcp"

    @classmethod
    def from_environment(cls) -> "TransportConfig":
        """Load configuration from environment variables.

        Environment variables:
            MCP_TRANSPORT: Transport type (stdio, streamable-http, websocket). Defaults to stdio.
            MCP_PORT: Port number for Streamable HTTP/WebSocket transports (required for non-stdio).
            MCP_HOST: Host address to bind to (default: 0.0.0.0).
            MCP_PATH: Path for HTTP endpoints (default: /mcp).

        Returns:
            TransportConfig instance

        Raises:
            ValueError: If transport type is invalid or port is missing/invalid for non-stdio
        """
        transport_str = os.getenv("MCP_TRANSPORT", "stdio").lower()

        # Support legacy http-sse for backward compatibility, map to streamable-http
        if transport_str == "http-sse":
            transport_str = "streamable-http"

        try:
            transport_type = TransportType(transport_str)
        except ValueError:
            raise ValueError(
                f"Invalid MCP_TRANSPORT: {transport_str}. "
                f"Valid values: stdio, streamable-http, websocket"
            )

        port = None
        if transport_type in (TransportType.STREAMABLE_HTTP, TransportType.WEBSOCKET):
            port_str = os.getenv("MCP_PORT")
            if not port_str:
                raise ValueError(
                    f"MCP_PORT environment variable required for {transport_str} transport"
                )
            try:
                port = int(port_str)
            except ValueError:
                raise ValueError(f"Invalid MCP_PORT value: {port_str}. Must be an integer.")

        host = os.getenv("MCP_HOST", "0.0.0.0")  # nosec B104  # Configurable via env var
        path = os.getenv("MCP_PATH", "/mcp")

        config = cls(transport_type=transport_type, port=port, host=host, path=path)
        config.validate()
        return config

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.transport_type in (TransportType.STREAMABLE_HTTP, TransportType.WEBSOCKET):
            if self.port is None:
                raise ValueError(f"Port required for {self.transport_type.value} transport")
            if not (1024 <= self.port <= 65535):
                raise ValueError(f"Port must be between 1024 and 65535, got {self.port}")
