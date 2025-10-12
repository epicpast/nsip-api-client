"""
Unit tests for transport configuration

Tests:
- TransportConfig.from_environment() with different MCP_TRANSPORT values
- Port validation (1024-65535 range)
- Error cases (invalid transport, missing port for HTTP SSE/WebSocket)
- TransportType enum validation
- Configuration validation rules

Target: >90% coverage (SC-011)
"""

import os
from unittest.mock import patch

import pytest

from nsip_mcp.transport import TransportConfig, TransportType


class TestTransportType:
    """Tests for TransportType enum."""

    def test_valid_transport_types(self):
        """Verify TransportType enum has stdio, streamable-http, websocket."""
        assert TransportType.STDIO.value == "stdio"
        assert TransportType.STREAMABLE_HTTP.value == "streamable-http"
        assert TransportType.WEBSOCKET.value == "websocket"

    def test_transport_type_from_string(self):
        """Verify TransportType can be created from string values."""
        assert TransportType("stdio") == TransportType.STDIO
        assert TransportType("streamable-http") == TransportType.STREAMABLE_HTTP
        assert TransportType("websocket") == TransportType.WEBSOCKET

    def test_transport_type_invalid_value(self):
        """Verify invalid transport type string raises ValueError."""
        with pytest.raises(ValueError):
            TransportType("invalid")


class TestTransportConfig:
    """Tests for TransportConfig dataclass."""

    @patch.dict(os.environ, {"MCP_TRANSPORT": "stdio"}, clear=True)
    def test_from_environment_stdio(self):
        """Verify from_environment() correctly parses MCP_TRANSPORT=stdio."""
        config = TransportConfig.from_environment()
        assert config.transport_type == TransportType.STDIO
        assert config.port is None

    @patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http", "MCP_PORT": "8080"}, clear=True)
    def test_from_environment_http_sse(self):
        """Verify from_environment() correctly parses MCP_TRANSPORT=streamable-http."""
        config = TransportConfig.from_environment()
        assert config.transport_type == TransportType.STREAMABLE_HTTP
        assert config.port == 8080

    @patch.dict(os.environ, {"MCP_TRANSPORT": "websocket", "MCP_PORT": "9000"}, clear=True)
    def test_from_environment_websocket(self):
        """Verify from_environment() correctly parses MCP_TRANSPORT=websocket."""
        config = TransportConfig.from_environment()
        assert config.transport_type == TransportType.WEBSOCKET
        assert config.port == 9000

    @patch.dict(os.environ, {}, clear=True)
    def test_from_environment_default_stdio(self):
        """Verify from_environment() defaults to stdio when MCP_TRANSPORT unset."""
        config = TransportConfig.from_environment()
        assert config.transport_type == TransportType.STDIO
        assert config.port is None

    @patch.dict(os.environ, {"MCP_TRANSPORT": "STDIO"}, clear=True)
    def test_from_environment_case_insensitive(self):
        """Verify MCP_TRANSPORT value is case-insensitive."""
        config = TransportConfig.from_environment()
        assert config.transport_type == TransportType.STDIO

    @patch.dict(os.environ, {"MCP_TRANSPORT": "STREAMABLE-HTTP", "MCP_PORT": "3000"}, clear=True)
    def test_from_environment_uppercase(self):
        """Verify uppercase transport values are handled correctly."""
        config = TransportConfig.from_environment()
        assert config.transport_type == TransportType.STREAMABLE_HTTP
        assert config.port == 3000

    @patch.dict(os.environ, {"MCP_TRANSPORT": "http-sse", "MCP_PORT": "8080"}, clear=True)
    def test_backward_compatibility_http_sse(self):
        """Verify legacy http-sse is mapped to streamable-http for backward compatibility."""
        config = TransportConfig.from_environment()
        assert config.transport_type == TransportType.STREAMABLE_HTTP
        assert config.port == 8080


class TestPortValidation:
    """Tests for port validation (1024-65535 range)."""

    @patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http", "MCP_PORT": "1024"}, clear=True)
    def test_valid_port_lower_bound(self):
        """Verify port 1024 (lower bound) is accepted."""
        config = TransportConfig.from_environment()
        assert config.port == 1024

    @patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http", "MCP_PORT": "65535"}, clear=True)
    def test_valid_port_upper_bound(self):
        """Verify port 65535 (upper bound) is accepted."""
        config = TransportConfig.from_environment()
        assert config.port == 65535

    @patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http", "MCP_PORT": "8080"}, clear=True)
    def test_valid_port_mid_range(self):
        """Verify port in mid-range (8080) is accepted."""
        config = TransportConfig.from_environment()
        assert config.port == 8080

    @patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http", "MCP_PORT": "1023"}, clear=True)
    def test_invalid_port_too_low(self):
        """Verify ports <1024 are rejected."""
        with pytest.raises(ValueError, match="Port must be between 1024 and 65535"):
            TransportConfig.from_environment()

    @patch.dict(os.environ, {"MCP_TRANSPORT": "websocket", "MCP_PORT": "65536"}, clear=True)
    def test_invalid_port_too_high(self):
        """Verify ports >65535 are rejected."""
        with pytest.raises(ValueError, match="Port must be between 1024 and 65535"):
            TransportConfig.from_environment()

    @patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http", "MCP_PORT": "0"}, clear=True)
    def test_invalid_port_zero(self):
        """Verify port 0 is rejected."""
        with pytest.raises(ValueError, match="Port must be between 1024 and 65535"):
            TransportConfig.from_environment()

    @patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http"}, clear=True)
    def test_port_required_for_http_sse(self):
        """Verify MCP_PORT required when MCP_TRANSPORT=streamable-http."""
        with pytest.raises(ValueError, match="MCP_PORT environment variable required"):
            TransportConfig.from_environment()

    @patch.dict(os.environ, {"MCP_TRANSPORT": "websocket"}, clear=True)
    def test_port_required_for_websocket(self):
        """Verify MCP_PORT required when MCP_TRANSPORT=websocket."""
        with pytest.raises(ValueError, match="MCP_PORT environment variable required"):
            TransportConfig.from_environment()

    @patch.dict(os.environ, {"MCP_TRANSPORT": "stdio"}, clear=True)
    def test_port_not_required_for_stdio(self):
        """Verify MCP_PORT not required when MCP_TRANSPORT=stdio."""
        config = TransportConfig.from_environment()
        assert config.transport_type == TransportType.STDIO
        assert config.port is None


class TestErrorCases:
    """Tests for error handling in transport configuration."""

    @patch.dict(os.environ, {"MCP_TRANSPORT": "invalid"}, clear=True)
    def test_invalid_transport_value(self):
        """Verify invalid MCP_TRANSPORT value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid MCP_TRANSPORT: invalid"):
            TransportConfig.from_environment()

    @patch.dict(os.environ, {"MCP_TRANSPORT": "grpc"}, clear=True)
    def test_unsupported_transport(self):
        """Verify unsupported transport raises ValueError with valid options."""
        with pytest.raises(ValueError, match="Valid values: stdio, streamable-http, websocket"):
            TransportConfig.from_environment()

    @patch.dict(os.environ, {"MCP_TRANSPORT": "websocket", "MCP_PORT": "abc"}, clear=True)
    def test_invalid_port_format(self):
        """Verify non-numeric MCP_PORT raises ValueError."""
        with pytest.raises(ValueError, match="Invalid MCP_PORT value: abc"):
            TransportConfig.from_environment()

    @patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http", "MCP_PORT": "80.5"}, clear=True)
    def test_invalid_port_float(self):
        """Verify float MCP_PORT raises ValueError."""
        with pytest.raises(ValueError, match="Invalid MCP_PORT value"):
            TransportConfig.from_environment()

    @patch.dict(os.environ, {"MCP_TRANSPORT": "streamable-http", "MCP_PORT": ""}, clear=True)
    def test_empty_port_value(self):
        """Verify empty MCP_PORT raises ValueError."""
        with pytest.raises(ValueError, match="MCP_PORT environment variable required"):
            TransportConfig.from_environment()


class TestConfigValidation:
    """Tests for TransportConfig.validate() method."""

    def test_validate_stdio_no_port(self):
        """Verify stdio config without port passes validation."""
        config = TransportConfig(transport_type=TransportType.STDIO)
        config.validate()  # Should not raise

    def test_validate_http_sse_with_port(self):
        """Verify Streamable HTTP config with valid port passes validation."""
        config = TransportConfig(transport_type=TransportType.STREAMABLE_HTTP, port=8080)
        config.validate()  # Should not raise

    def test_validate_websocket_with_port(self):
        """Verify WebSocket config with valid port passes validation."""
        config = TransportConfig(transport_type=TransportType.WEBSOCKET, port=9000)
        config.validate()  # Should not raise

    def test_validate_http_sse_missing_port(self):
        """Verify Streamable HTTP config without port fails validation."""
        config = TransportConfig(transport_type=TransportType.STREAMABLE_HTTP)
        with pytest.raises(ValueError, match="Port required for streamable-http transport"):
            config.validate()

    def test_validate_websocket_missing_port(self):
        """Verify WebSocket config without port fails validation."""
        config = TransportConfig(transport_type=TransportType.WEBSOCKET)
        with pytest.raises(ValueError, match="Port required for websocket transport"):
            config.validate()

    def test_validate_invalid_port_range(self):
        """Verify invalid port range fails validation."""
        config = TransportConfig(transport_type=TransportType.STREAMABLE_HTTP, port=500)
        with pytest.raises(ValueError, match="Port must be between 1024 and 65535"):
            config.validate()
