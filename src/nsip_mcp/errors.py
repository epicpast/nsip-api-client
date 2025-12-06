"""Error handling and structured error responses for MCP protocol.

This module defines error codes, error data structures, and error response models
that comply with JSON-RPC 2.0 specification and provide LLM-friendly error messages.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class McpErrorCode(IntEnum):
    """MCP error codes following JSON-RPC 2.0 specification.

    Standard JSON-RPC 2.0 error codes (-32700 to -32603):
    - Parse error: Invalid JSON
    - Invalid request: JSON structure invalid
    - Method not found: Unknown method
    - Invalid params: Invalid method parameters
    - Internal error: Server internal error

    Custom error codes (-32000 to -32099):
    - NSIP API errors
    - Cache errors
    - Summarization errors
    - Validation errors
    """

    # JSON-RPC 2.0 standard errors
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603

    # Custom MCP errors
    NSIP_API_ERROR = -32000
    CACHE_ERROR = -32001
    SUMMARIZATION_ERROR = -32002
    VALIDATION_ERROR = -32003
    TIMEOUT_ERROR = -32004


@dataclass
class McpErrorData:
    """Structured error data for LLM-friendly error messages.

    Attributes:
        parameter: Name of the parameter that caused the error (if applicable)
        value: Invalid value provided
        expected: Expected format or value
        suggestion: Actionable suggestion for fixing the error
        retry_after: Seconds to wait before retrying (for rate limiting)
    """

    parameter: str | None = None
    value: Any | None = None
    expected: str | None = None
    suggestion: str | None = None
    retry_after: Any | None = None  # Can be int or str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization.

        Returns:
            Dict with only non-None fields
        """
        result = {}
        if self.parameter is not None:
            result["parameter"] = self.parameter
        if self.value is not None:
            result["value"] = self.value
        if self.expected is not None:
            result["expected"] = self.expected
        if self.suggestion is not None:
            result["suggestion"] = self.suggestion
        if self.retry_after is not None:
            result["retry_after"] = self.retry_after
        return result


@dataclass
class McpErrorResponse:
    """MCP error response following JSON-RPC 2.0 format.

    Attributes:
        code: Error code (JSON-RPC 2.0 or custom)
        message: Human-readable error message
        data: Optional structured error data with suggestions
    """

    code: int
    message: str
    data: McpErrorData | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-RPC 2.0 error format.

        Returns:
            Dict in JSON-RPC 2.0 error format

        Example:
            {
                "code": -32602,
                "message": "Invalid parameter: lpn_id",
                "data": {
                    "parameter": "lpn_id",
                    "value": "123",
                    "expected": "Minimum 5 characters",
                    "suggestion": "Provide full LPN ID (e.g., '6####92020###249')"
                }
            }
        """
        result = {"code": self.code, "message": self.message}
        if self.data:
            result["data"] = self.data.to_dict()
        return result

    @classmethod
    def invalid_params(
        cls,
        parameter: str,
        value: Any,
        expected: str,
        suggestion: str,
    ) -> "McpErrorResponse":
        """Create invalid parameters error (JSON-RPC -32602).

        Args:
            parameter: Name of the invalid parameter
            value: Invalid value provided
            expected: Expected format or value
            suggestion: Actionable suggestion for fixing the error

        Returns:
            McpErrorResponse for invalid parameters

        Example:
            >>> error = McpErrorResponse.invalid_params(
            ...     parameter="lpn_id",
            ...     value="123",
            ...     expected="Minimum 5 characters",
            ...     suggestion="Provide full LPN ID"
            ... )
            >>> error.code
            -32602
        """
        data = McpErrorData(
            parameter=parameter, value=value, expected=expected, suggestion=suggestion
        )
        return cls(
            code=McpErrorCode.INVALID_PARAMS,
            message=f"Invalid parameter: {parameter}",
            data=data,
        )

    @classmethod
    def nsip_api_error(cls, message: str, original_error: str | None = None) -> "McpErrorResponse":
        """Create NSIP API error (-32000).

        Args:
            message: Error message describing what went wrong
            original_error: Original error message from NSIP API

        Returns:
            McpErrorResponse for NSIP API errors

        Example:
            >>> error = McpErrorResponse.nsip_api_error(
            ...     message="Animal not found",
            ...     original_error="404 Not Found"
            ... )
            >>> error.code
            -32000
        """
        suggestion = "Verify the LPN ID is correct and try again"
        if original_error and "timeout" in original_error.lower():
            suggestion = "The NSIP API is experiencing delays. Wait 30 seconds and retry"

        data = McpErrorData(
            suggestion=suggestion,
            value=original_error if original_error else None,
        )
        return cls(code=McpErrorCode.NSIP_API_ERROR, message=message, data=data)

    @classmethod
    def cache_error(cls, message: str) -> "McpErrorResponse":
        """Create cache error (-32001).

        Args:
            message: Error message describing cache failure

        Returns:
            McpErrorResponse for cache errors

        Note:
            Cache errors are typically non-fatal and handled by bypassing cache
        """
        data = McpErrorData(suggestion="Cache temporarily unavailable, using direct API call")
        return cls(code=McpErrorCode.CACHE_ERROR, message=message, data=data)

    @classmethod
    def summarization_error(cls, message: str) -> "McpErrorResponse":
        """Create summarization error (-32002).

        Args:
            message: Error message describing summarization failure

        Returns:
            McpErrorResponse for summarization errors

        Note:
            Summarization errors are handled by falling back to pass-through
        """
        data = McpErrorData(
            suggestion="Summarization failed, returning full response (may exceed token limits)"
        )
        return cls(code=McpErrorCode.SUMMARIZATION_ERROR, message=message, data=data)

    @classmethod
    def validation_error(cls, field: str, message: str) -> "McpErrorResponse":
        """Create validation error (-32003).

        Args:
            field: Name of the field that failed validation
            message: Validation error message

        Returns:
            McpErrorResponse for validation errors
        """
        data = McpErrorData(parameter=field, suggestion=f"Check {field} format and try again")
        return cls(code=McpErrorCode.VALIDATION_ERROR, message=message, data=data)
