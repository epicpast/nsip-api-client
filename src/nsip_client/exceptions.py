"""
Custom exceptions for the NSIP API client.

Exception hierarchy:
    NSIPError
    ├── NSIPAPIError (status_code, response)
    │   └── NSIPNotFoundError (search_string, always 404)
    ├── NSIPConnectionError
    ├── NSIPTimeoutError
    └── NSIPValidationError
"""


class NSIPError(Exception):
    """Base exception for all NSIP client errors."""

    pass


class NSIPAPIError(NSIPError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class NSIPNotFoundError(NSIPAPIError):
    """Raised when an animal or resource is not found."""

    def __init__(self, message: str, search_string: str | None = None) -> None:
        super().__init__(message, status_code=404)
        self.search_string = search_string


class NSIPConnectionError(NSIPError):
    """Raised when connection to the API fails."""

    pass


class NSIPTimeoutError(NSIPError):
    """Raised when a request times out."""

    pass


class NSIPValidationError(NSIPError):
    """Raised when request parameters are invalid."""

    pass
