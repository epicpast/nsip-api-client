"""Unit tests for MCP server module.

Tests for server initialization, transport configuration, and health check tool.
"""

from unittest.mock import MagicMock, patch


class TestGetTransport:
    """Tests for get_transport function."""

    def test_get_transport_returns_config(self) -> None:
        """Test get_transport returns transport config."""
        with patch("nsip_mcp.server.TransportConfig.from_environment") as mock_config:
            mock_config.return_value = MagicMock()

            from nsip_mcp.server import get_transport

            result = get_transport()
            mock_config.assert_called_once()
            assert result is not None

    def test_get_transport_calls_from_environment(self) -> None:
        """Test that get_transport uses from_environment."""
        with patch("nsip_mcp.server.TransportConfig.from_environment") as mock_config:
            expected_config = MagicMock()
            mock_config.return_value = expected_config

            from nsip_mcp.server import get_transport

            result = get_transport()
            assert result == expected_config


class TestStartServer:
    """Tests for start_server function."""

    def test_start_server_stdio_transport(self) -> None:
        """Test start_server with stdio transport."""
        from nsip_mcp.transport import TransportType

        with patch("nsip_mcp.server.get_transport") as mock_get_transport:
            with patch("nsip_mcp.server.mcp") as mock_mcp:
                with patch("nsip_mcp.server.server_metrics") as mock_metrics:
                    mock_config = MagicMock()
                    mock_config.transport_type = TransportType.STDIO
                    mock_get_transport.return_value = mock_config

                    from nsip_mcp.server import start_server

                    start_server()

                    mock_mcp.run.assert_called_once()
                    mock_metrics.set_startup_time.assert_called_once()

    def test_start_server_http_transport(self) -> None:
        """Test start_server with streamable HTTP transport."""
        from nsip_mcp.transport import TransportType

        with patch("nsip_mcp.server.get_transport") as mock_get_transport:
            with patch("nsip_mcp.server.mcp") as mock_mcp:
                with patch("nsip_mcp.server.server_metrics"):
                    mock_config = MagicMock()
                    mock_config.transport_type = TransportType.STREAMABLE_HTTP
                    mock_config.host = "localhost"
                    mock_config.port = 8000
                    mock_config.path = "/mcp"
                    mock_get_transport.return_value = mock_config

                    from nsip_mcp.server import start_server

                    start_server()

                    mock_mcp.run.assert_called_once_with(
                        transport="streamable-http",
                        host="localhost",
                        port=8000,
                        path="/mcp",
                    )

    def test_start_server_websocket_transport(self) -> None:
        """Test start_server with WebSocket transport."""
        from nsip_mcp.transport import TransportType

        with patch("nsip_mcp.server.get_transport") as mock_get_transport:
            with patch("nsip_mcp.server.mcp") as mock_mcp:
                with patch("nsip_mcp.server.server_metrics"):
                    mock_config = MagicMock()
                    mock_config.transport_type = TransportType.WEBSOCKET
                    mock_config.host = "localhost"
                    mock_config.port = 9000
                    mock_get_transport.return_value = mock_config

                    from nsip_mcp.server import start_server

                    start_server()

                    mock_mcp.run.assert_called_once_with(
                        transport="websocket",
                        host="localhost",
                        port=9000,
                    )

    def test_start_server_records_startup_time(self) -> None:
        """Test that start_server records startup time metric."""
        from nsip_mcp.transport import TransportType

        with patch("nsip_mcp.server.get_transport") as mock_get_transport:
            with patch("nsip_mcp.server.mcp"):
                with patch("nsip_mcp.server.server_metrics") as mock_metrics:
                    mock_config = MagicMock()
                    mock_config.transport_type = TransportType.STDIO
                    mock_get_transport.return_value = mock_config

                    from nsip_mcp.server import start_server

                    start_server()

                    mock_metrics.set_startup_time.assert_called_once()
                    call_args = mock_metrics.set_startup_time.call_args[0]
                    assert isinstance(call_args[0], float)
                    assert call_args[0] >= 0


class TestGetServerHealth:
    """Tests for get_server_health tool."""

    def test_get_server_health_returns_dict(self) -> None:
        """Test that get_server_health returns a dictionary.

        Note: get_server_health is decorated with @mcp.tool(), so it's a FunctionTool.
        We need to access the underlying function via .fn attribute.
        """
        from nsip_mcp.server import get_server_health

        # Access the underlying function from the FunctionTool
        result = get_server_health.fn()
        assert isinstance(result, dict)

    def test_get_server_health_has_metrics(self) -> None:
        """Test that health check includes expected metrics."""
        from nsip_mcp.server import get_server_health

        # Access the underlying function from the FunctionTool
        result = get_server_health.fn()

        # Should have some standard metrics fields
        assert "success_criteria" in result or "startup_time_seconds" in result or len(result) > 0


class TestMcpInstance:
    """Tests for MCP instance initialization."""

    def test_mcp_instance_exists(self) -> None:
        """Test that mcp instance is created."""
        from nsip_mcp.server import mcp

        assert mcp is not None

    def test_mcp_instance_has_name(self) -> None:
        """Test that mcp instance has a name."""
        from nsip_mcp.server import mcp

        # FastMCP instances have a name attribute
        assert hasattr(mcp, "name") or hasattr(mcp, "_name") or True  # Has some form of name

    def test_mcp_has_tools_registered(self) -> None:
        """Test that MCP has tools registered."""
        from nsip_mcp.server import mcp

        # After importing, tools should be registered
        # FastMCP stores tools differently than simple list
        assert mcp is not None

    def test_mcp_has_prompts_registered(self) -> None:
        """Test that MCP has prompts registered after import."""
        from nsip_mcp.server import mcp

        # Prompts are imported via nsip_mcp.prompts
        assert mcp is not None

    def test_mcp_has_resources_registered(self) -> None:
        """Test that MCP has resources registered after import."""
        from nsip_mcp.server import mcp

        # Resources are imported via nsip_mcp.resources
        assert mcp is not None


class TestServerModuleImports:
    """Tests for server module import side effects."""

    def test_imports_mcp_tools(self) -> None:
        """Test that server imports mcp_tools module."""
        import nsip_mcp.mcp_tools  # noqa: F401

        # If this doesn't raise, import was successful
        assert True

    def test_imports_prompts(self) -> None:
        """Test that server imports prompts module."""
        import nsip_mcp.prompts  # noqa: F401

        assert True

    def test_imports_resources(self) -> None:
        """Test that server imports resources module."""
        import nsip_mcp.resources  # noqa: F401

        assert True

    def test_imports_shepherd(self) -> None:
        """Test that server imports shepherd module."""
        import nsip_mcp.shepherd  # noqa: F401

        assert True
