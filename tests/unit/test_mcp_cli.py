"""Tests for the NSIP MCP Server CLI module.

Tests exception handling paths in the CLI entry point.
"""

from unittest.mock import patch

import pytest


class TestMcpCli:
    """Tests for nsip_mcp.cli exception handling paths."""

    def test_main_clean_shutdown(self, capsys):
        """Test that KeyboardInterrupt causes clean shutdown with exit code 0."""
        with patch("nsip_mcp.cli.start_server") as mock_start:
            mock_start.side_effect = KeyboardInterrupt()

            from nsip_mcp.cli import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert "Server stopped by user" in captured.out

    def test_main_configuration_error(self, capsys):
        """Test that ValueError causes exit code 1 with configuration error message."""
        with patch("nsip_mcp.cli.start_server") as mock_start:
            mock_start.side_effect = ValueError("Invalid transport type: foobar")

            from nsip_mcp.cli import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

            captured = capsys.readouterr()
            assert "Configuration error:" in captured.err
            assert "Invalid transport type: foobar" in captured.err

    def test_main_runtime_error(self, capsys):
        """Test that generic Exception causes exit code 1 with server error message."""
        with patch("nsip_mcp.cli.start_server") as mock_start:
            mock_start.side_effect = RuntimeError("Unexpected server failure")

            from nsip_mcp.cli import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

            captured = capsys.readouterr()
            assert "Server error:" in captured.err
            assert "Unexpected server failure" in captured.err

    def test_main_os_error(self, capsys):
        """Test that OSError (e.g., port in use) is handled as server error."""
        with patch("nsip_mcp.cli.start_server") as mock_start:
            mock_start.side_effect = OSError("Address already in use")

            from nsip_mcp.cli import main

            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

            captured = capsys.readouterr()
            assert "Server error:" in captured.err
            assert "Address already in use" in captured.err

    def test_main_module_entrypoint_exists(self):
        """Test that CLI module can be used as entrypoint."""
        import nsip_mcp.cli

        assert hasattr(nsip_mcp.cli, "main")
        assert callable(nsip_mcp.cli.main)
