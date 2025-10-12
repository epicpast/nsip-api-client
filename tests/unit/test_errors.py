"""Unit tests for error handling infrastructure.

Tests McpErrorCode, McpErrorData, and McpErrorResponse models to ensure
structured error responses comply with JSON-RPC 2.0 specification.
"""

from nsip_mcp.errors import McpErrorCode, McpErrorData, McpErrorResponse


class TestMcpErrorCode:
    """Tests for McpErrorCode enum."""

    def test_standard_json_rpc_codes(self):
        """Verify JSON-RPC 2.0 standard error codes."""
        assert McpErrorCode.PARSE_ERROR == -32700
        assert McpErrorCode.INVALID_REQUEST == -32600
        assert McpErrorCode.METHOD_NOT_FOUND == -32601
        assert McpErrorCode.INVALID_PARAMS == -32602
        assert McpErrorCode.INTERNAL_ERROR == -32603

    def test_custom_error_codes(self):
        """Verify custom MCP error codes in -32000 to -32099 range."""
        assert McpErrorCode.NSIP_API_ERROR == -32000
        assert McpErrorCode.CACHE_ERROR == -32001
        assert McpErrorCode.SUMMARIZATION_ERROR == -32002
        assert McpErrorCode.VALIDATION_ERROR == -32003
        assert McpErrorCode.TIMEOUT_ERROR == -32004

        # Verify all custom codes in valid range
        custom_codes = [
            McpErrorCode.NSIP_API_ERROR,
            McpErrorCode.CACHE_ERROR,
            McpErrorCode.SUMMARIZATION_ERROR,
            McpErrorCode.VALIDATION_ERROR,
            McpErrorCode.TIMEOUT_ERROR,
        ]
        for code in custom_codes:
            assert -32099 <= code <= -32000


class TestMcpErrorData:
    """Tests for McpErrorData model."""

    def test_to_dict_all_fields(self):
        """Verify to_dict includes all non-None fields."""
        data = McpErrorData(
            parameter="lpn_id",
            value="123",
            expected="Minimum 5 characters",
            suggestion="Provide full LPN ID",
            retry_after=30,
        )

        result = data.to_dict()

        assert result["parameter"] == "lpn_id"
        assert result["value"] == "123"
        assert result["expected"] == "Minimum 5 characters"
        assert result["suggestion"] == "Provide full LPN ID"
        assert result["retry_after"] == 30

    def test_to_dict_omits_none_values(self):
        """Verify to_dict omits None fields."""
        data = McpErrorData(
            parameter="breed_id",
            suggestion="Use valid breed ID",
        )

        result = data.to_dict()

        assert result["parameter"] == "breed_id"
        assert result["suggestion"] == "Use valid breed ID"
        assert "value" not in result
        assert "expected" not in result
        assert "retry_after" not in result

    def test_to_dict_empty_data(self):
        """Verify to_dict handles all None fields."""
        data = McpErrorData()
        result = data.to_dict()
        assert result == {}


class TestMcpErrorResponse:
    """Tests for McpErrorResponse model."""

    def test_to_dict_basic_structure(self):
        """Verify to_dict produces JSON-RPC 2.0 error format."""
        error = McpErrorResponse(
            code=McpErrorCode.INVALID_PARAMS,
            message="Invalid parameter: lpn_id",
        )

        result = error.to_dict()

        assert result["code"] == -32602
        assert result["message"] == "Invalid parameter: lpn_id"
        assert "data" not in result  # No data provided

    def test_to_dict_with_data(self):
        """Verify to_dict includes error data when provided."""
        data = McpErrorData(parameter="lpn_id", value="123", suggestion="Provide full LPN ID")
        error = McpErrorResponse(
            code=McpErrorCode.INVALID_PARAMS, message="Invalid parameter: lpn_id", data=data
        )

        result = error.to_dict()

        assert result["code"] == -32602
        assert result["message"] == "Invalid parameter: lpn_id"
        assert "data" in result
        assert result["data"]["parameter"] == "lpn_id"
        assert result["data"]["value"] == "123"
        assert result["data"]["suggestion"] == "Provide full LPN ID"

    def test_invalid_params_factory(self):
        """Verify invalid_params factory method."""
        error = McpErrorResponse.invalid_params(
            parameter="lpn_id",
            value="123",
            expected="Minimum 5 characters",
            suggestion="Provide full LPN ID (e.g., '6401492020FLE249')",
        )

        assert error.code == McpErrorCode.INVALID_PARAMS
        assert error.message == "Invalid parameter: lpn_id"
        assert error.data is not None
        assert error.data.parameter == "lpn_id"
        assert error.data.value == "123"
        assert error.data.expected == "Minimum 5 characters"
        assert "6401492020FLE249" in error.data.suggestion

        # Verify serialization
        result = error.to_dict()
        assert result["code"] == -32602
        assert "suggestion" in result["data"]

    def test_nsip_api_error_factory(self):
        """Verify nsip_api_error factory method."""
        error = McpErrorResponse.nsip_api_error(
            message="Animal not found", original_error="404 Not Found"
        )

        assert error.code == McpErrorCode.NSIP_API_ERROR
        assert error.message == "Animal not found"
        assert error.data is not None
        assert error.data.suggestion is not None
        assert "LPN ID" in error.data.suggestion

    def test_nsip_api_error_timeout_suggestion(self):
        """Verify nsip_api_error provides timeout-specific suggestion."""
        error = McpErrorResponse.nsip_api_error(
            message="Request failed", original_error="Request timeout after 30s"
        )

        assert error.code == McpErrorCode.NSIP_API_ERROR
        assert error.data is not None
        # Timeout suggestion should include delay/wait guidance and retry
        suggestion_lower = error.data.suggestion.lower()
        assert "wait" in suggestion_lower or "delay" in suggestion_lower
        assert "retry" in suggestion_lower or "30 seconds" in error.data.suggestion

    def test_cache_error_factory(self):
        """Verify cache_error factory method."""
        error = McpErrorResponse.cache_error(message="Cache storage failed")

        assert error.code == McpErrorCode.CACHE_ERROR
        assert error.message == "Cache storage failed"
        assert error.data is not None
        assert "cache" in error.data.suggestion.lower()

    def test_summarization_error_factory(self):
        """Verify summarization_error factory method."""
        error = McpErrorResponse.summarization_error(message="Token counting failed")

        assert error.code == McpErrorCode.SUMMARIZATION_ERROR
        assert error.message == "Token counting failed"
        assert error.data is not None
        assert "full response" in error.data.suggestion.lower()

    def test_validation_error_factory(self):
        """Verify validation_error factory method."""
        error = McpErrorResponse.validation_error(
            field="search_string", message="Search string too short"
        )

        assert error.code == McpErrorCode.VALIDATION_ERROR
        assert error.message == "Search string too short"
        assert error.data is not None
        assert error.data.parameter == "search_string"
        assert "search_string" in error.data.suggestion


class TestErrorResponseSerialization:
    """Tests for error response JSON serialization."""

    def test_serialization_produces_valid_json_rpc(self):
        """Verify serialized error matches JSON-RPC 2.0 spec."""
        error = McpErrorResponse.invalid_params(
            parameter="page",
            value=-1,
            expected="Non-negative integer",
            suggestion="Use page=0 for first page",
        )

        result = error.to_dict()

        # JSON-RPC 2.0 error object requirements
        assert "code" in result
        assert "message" in result
        assert isinstance(result["code"], int)
        assert isinstance(result["message"], str)

        # Data is optional but should be dict if present
        if "data" in result:
            assert isinstance(result["data"], dict)

    def test_error_data_contains_actionable_suggestions(self):
        """Verify all error factories include actionable suggestions."""
        errors = [
            McpErrorResponse.invalid_params("lpn_id", "123", "Min 5 chars", "Provide full ID"),
            McpErrorResponse.nsip_api_error("Failed", "404"),
            McpErrorResponse.cache_error("Cache down"),
            McpErrorResponse.summarization_error("Token fail"),
            McpErrorResponse.validation_error("field", "Invalid"),
        ]

        for error in errors:
            result = error.to_dict()
            if "data" in result:
                assert "suggestion" in result["data"]
                assert len(result["data"]["suggestion"]) > 0

    def test_nested_dict_structure(self):
        """Verify complete nested structure for complex error."""
        error = McpErrorResponse.invalid_params(
            parameter="page_size",
            value=200,
            expected="Integer between 1 and 100",
            suggestion="Use page_size between 1-100 (e.g., 15), not 200",
        )

        result = error.to_dict()

        # Verify complete structure
        assert result == {
            "code": -32602,
            "message": "Invalid parameter: page_size",
            "data": {
                "parameter": "page_size",
                "value": 200,
                "expected": "Integer between 1 and 100",
                "suggestion": "Use page_size between 1-100 (e.g., 15), not 200",
            },
        }
