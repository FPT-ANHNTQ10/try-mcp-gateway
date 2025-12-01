"""Custom exception definitions for the monitoring MCP server."""


class MonitoringError(Exception):
    """Base exception for monitoring-related errors."""

    pass


class DataLoadError(MonitoringError):
    """Raised when data cannot be loaded from YAML files."""

    pass


class ConfigurationError(MonitoringError):
    """Raised when configuration is invalid or missing."""

    pass


class ToolExecutionError(MonitoringError):
    """Raised when a tool fails during execution."""

    pass


class ValidationError(MonitoringError):
    """Raised when input validation fails."""

    pass


class TimeRangeError(ValidationError):
    """Raised when time range parameters are invalid."""

    pass


class FilterError(ValidationError):
    """Raised when filter parameters are invalid."""

    pass
