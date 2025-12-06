"""
Specific exception classes for NSIP hooks.

Replaces generic `except Exception` with targeted error handling.
"""


class NSIPHookError(Exception):
    """Base exception for all NSIP hook errors."""

    def __init__(self, message: str, hook_name: str = None):
        self.message = message
        self.hook_name = hook_name
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.hook_name:
            return f"[{self.hook_name}] {self.message}"
        return self.message


class LPNValidationError(NSIPHookError):
    """Invalid LPN ID format."""

    def __init__(self, lpn_id: str, reason: str):
        self.lpn_id = lpn_id
        self.reason = reason
        super().__init__(
            f"Invalid LPN ID '{lpn_id}': {reason}",
            hook_name="LPNValidator"
        )


class CacheError(NSIPHookError):
    """Cache read/write failure."""

    def __init__(self, operation: str, path: str = None, cause: str = None):
        self.operation = operation
        self.path = path
        self.cause = cause
        message = f"Cache {operation} failed"
        if path:
            message += f" for {path}"
        if cause:
            message += f": {cause}"
        super().__init__(message, hook_name="Cache")


class CacheReadError(CacheError):
    """Failed to read from cache."""

    def __init__(self, path: str = None, cause: str = None):
        super().__init__("read", path, cause)


class CacheWriteError(CacheError):
    """Failed to write to cache."""

    def __init__(self, path: str = None, cause: str = None):
        super().__init__("write", path, cause)


class APIHealthError(NSIPHookError):
    """API health check failure."""

    def __init__(self, endpoint: str = None, status_code: int = None, cause: str = None):
        self.endpoint = endpoint
        self.status_code = status_code
        self.cause = cause

        message = "NSIP API health check failed"
        if endpoint:
            message += f" for {endpoint}"
        if status_code:
            message += f" (HTTP {status_code})"
        if cause:
            message += f": {cause}"

        super().__init__(message, hook_name="APIHealthCheck")


class RetryExhaustedError(NSIPHookError):
    """All retry attempts exhausted."""

    def __init__(self, tool_name: str, attempts: int, last_error: str = None):
        self.tool_name = tool_name
        self.attempts = attempts
        self.last_error = last_error

        message = f"All {attempts} retry attempts exhausted for {tool_name}"
        if last_error:
            message += f". Last error: {last_error}"

        super().__init__(message, hook_name="AutoRetry")


class ExportError(NSIPHookError):
    """Export operation failure."""

    def __init__(self, export_type: str, path: str = None, cause: str = None):
        self.export_type = export_type
        self.path = path
        self.cause = cause

        message = f"{export_type} export failed"
        if path:
            message += f" to {path}"
        if cause:
            message += f": {cause}"

        super().__init__(message, hook_name=f"{export_type}Exporter")


class PromptAnalysisError(NSIPHookError):
    """Prompt analysis failure."""

    def __init__(self, cause: str):
        super().__init__(f"Prompt analysis failed: {cause}", hook_name="PromptAnalyzer")


class HookInputError(NSIPHookError):
    """Invalid hook input data."""

    def __init__(self, expected: str, received: str = None):
        message = f"Invalid hook input: expected {expected}"
        if received:
            message += f", received {received}"
        super().__init__(message)
