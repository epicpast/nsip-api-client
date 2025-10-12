"""Transport configuration for MCP server.

This module handles transport mechanism selection and configuration for the MCP server,
supporting stdio (default), HTTP SSE, and WebSocket transports.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TransportType(Enum):
    """Supported MCP transport mechanisms."""

    STDIO = "stdio"
    HTTP_SSE = "http-sse"
    WEBSOCKET = "websocket"


@dataclass
class TransportConfig:
    """MCP server transport configuration.

    Attributes:
        transport_type: The transport mechanism to use
        port: Port number for HTTP SSE and WebSocket transports (required for non-stdio)
    """

    transport_type: TransportType
    port: Optional[int] = None

    @classmethod
    def from_environment(cls) -> "TransportConfig":
        """Load configuration from environment variables.

        Environment variables:
            MCP_TRANSPORT: Transport type (stdio, http-sse, websocket). Defaults to stdio.
            MCP_PORT: Port number for HTTP SSE/WebSocket transports (required for non-stdio).

        Returns:
            TransportConfig instance

        Raises:
            ValueError: If transport type is invalid or port is missing/invalid for non-stdio
        """
        transport_str = os.getenv("MCP_TRANSPORT", "stdio").lower()

        try:
            transport_type = TransportType(transport_str)
        except ValueError:
            raise ValueError(
                f"Invalid MCP_TRANSPORT: {transport_str}. "
                f"Valid values: stdio, http-sse, websocket"
            )

        port = None
        if transport_type in (TransportType.HTTP_SSE, TransportType.WEBSOCKET):
            port_str = os.getenv("MCP_PORT")
            if not port_str:
                raise ValueError(
                    f"MCP_PORT environment variable required for {transport_str} transport"
                )
            try:
                port = int(port_str)
            except ValueError:
                raise ValueError(f"Invalid MCP_PORT value: {port_str}. Must be an integer.")

        config = cls(transport_type=transport_type, port=port)
        config.validate()
        return config

    def validate(self) -> None:
        """Validate configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.transport_type in (TransportType.HTTP_SSE, TransportType.WEBSOCKET):
            if self.port is None:
                raise ValueError(f"Port required for {self.transport_type.value} transport")
            if not (1024 <= self.port <= 65535):
                raise ValueError(f"Port must be between 1024 and 65535, got {self.port}")
