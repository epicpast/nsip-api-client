"""
End-to-End Integration Tests for NSIP MCP Server

Minimal integration tests verifying critical integration points.
Comprehensive testing is covered by unit tests (60% coverage).
"""

import asyncio

import pytest

from nsip_mcp.cache import response_cache
from nsip_mcp.metrics import server_metrics
from nsip_mcp.server import mcp


class TestServerIntegration:
    """Test core server integration - tool discovery (SC-001)."""

    def test_all_tools_discoverable(self):
        """Verify all 15 MCP tools are discoverable."""
        tools_dict = asyncio.run(mcp.get_tools())

        # Should have 9 NSIP tools + 5 Shepherd tools + 1 health tool = 15 total
        assert len(tools_dict) == 15

        expected_tools = [
            # NSIP tools
            "nsip_get_last_update",
            "nsip_list_breeds",
            "nsip_get_statuses",
            "nsip_get_trait_ranges",
            "nsip_search_animals",
            "nsip_get_animal",
            "nsip_get_lineage",
            "nsip_get_progeny",
            "nsip_search_by_lpn",
            # Shepherd tools
            "shepherd_consult",
            "shepherd_breeding",
            "shepherd_health",
            "shepherd_calendar",
            "shepherd_economics",
            # Utility tools
            "get_server_health",
        ]

        for tool_name in expected_tools:
            assert tool_name in tools_dict, f"Tool '{tool_name}' not registered"

    def test_tools_have_metadata(self):
        """Verify all tools have required metadata."""
        tools_dict = asyncio.run(mcp.get_tools())

        for tool_name, tool in tools_dict.items():
            assert hasattr(tool, "name"), f"{tool_name} missing name"
            assert hasattr(tool, "description"), f"{tool_name} missing description"
            assert hasattr(tool, "fn"), f"{tool_name} missing fn"


class TestCacheIntegration:
    """Test cache integration."""

    def test_cache_set_and_get(self):
        """Verify basic cache operations work."""
        response_cache.clear()

        test_key = response_cache.make_key("test_op", p="v")
        test_value = {"result": "data"}

        # Set and retrieve
        response_cache.set(test_key, test_value)
        result = response_cache.get(test_key)

        assert result == test_value


class TestMetricsIntegration:
    """Test metrics integration."""

    def test_metrics_tracking(self):
        """Verify metrics can be tracked."""
        initial_attempts = server_metrics.validation_attempts

        server_metrics.record_validation(success=True)

        assert server_metrics.validation_attempts == initial_attempts + 1


@pytest.fixture(autouse=True)
def reset_state():
    """Reset state before each test."""
    response_cache.clear()
    yield
