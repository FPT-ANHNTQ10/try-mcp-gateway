"""
Exception classes for the MCP server.

This module defines custom exceptions for better error handling and debugging.
"""


class MCPServerError(Exception):
    """Base exception for MCP server errors."""

    def __init__(self, message: str, details: dict | None = None):
        """
        Initialize exception.

        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ToolExecutionError(MCPServerError):
    """Exception raised when a tool execution fails."""

    pass


class APIError(MCPServerError):
    """Exception raised when an external API call fails."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_text: str | None = None,
    ):
        """
        Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            response_text: Response body text
        """
        details = {}
        if status_code:
            details["status_code"] = status_code
        if response_text:
            details["response_text"] = response_text
        super().__init__(message, details)


class ValidationError(MCPServerError):
    """Exception raised when input validation fails."""

    pass


class ConfigurationError(MCPServerError):
    """Exception raised when configuration is invalid."""

    pass


class TimeoutError(MCPServerError):
    """Exception raised when an operation times out."""

    pass
