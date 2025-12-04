"""
Exception classes for ReServer Client SDK.
"""


class ReServerClientError(Exception):
    """Base exception for all ReServer client errors."""
    pass


class ReServerConnectionError(ReServerClientError):
    """Raised when connection to the server fails."""
    pass


class ReServerServerError(ReServerClientError):
    """Raised when the server returns an error."""
    
    def __init__(self, message: str, status_code: str | None = None):
        super().__init__(message)
        self.status_code = status_code


class ReServerTimeoutError(ReServerClientError):
    """Raised when a request times out."""
    pass


class ReServerValidationError(ReServerClientError):
    """Raised when input validation fails."""
    pass
