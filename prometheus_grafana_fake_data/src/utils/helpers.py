"""Helper functions for the monitoring MCP server."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# Export timedelta for use in other modules
__all__ = ["timedelta"]


def get_timestamp_range(
    hours: int = 1, end_time: Optional[datetime] = None
) -> tuple[datetime, datetime]:
    """
    Get start and end timestamp for a given time range.

    Args:
        hours: Number of hours to look back
        end_time: End time (defaults to current UTC time)

    Returns:
        Tuple of (start_time, end_time) as datetime objects
    """
    if end_time is None:
        end_time = datetime.now(timezone.utc)

    start_time = end_time - timedelta(hours=hours)
    return start_time, end_time


def parse_iso_timestamp(timestamp_str: str) -> datetime:
    """
    Parse ISO 8601 timestamp string to datetime.

    Args:
        timestamp_str: ISO 8601 formatted timestamp string

    Returns:
        datetime object in UTC
    """
    # Handle both with and without 'Z'
    if timestamp_str.endswith("Z"):
        timestamp_str = timestamp_str[:-1] + "+00:00"

    return datetime.fromisoformat(timestamp_str)


def is_in_time_range(
    timestamp_str: str, start_time: datetime, end_time: datetime
) -> bool:
    """
    Check if a timestamp falls within a given time range.

    Args:
        timestamp_str: ISO 8601 formatted timestamp string
        start_time: Start of time range
        end_time: End of time range

    Returns:
        True if timestamp is within range, False otherwise
    """
    try:
        timestamp = parse_iso_timestamp(timestamp_str)
        return start_time <= timestamp <= end_time
    except (ValueError, AttributeError):
        return False


def format_duration(seconds: Optional[int]) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "2h 30m 45s")
    """
    if seconds is None:
        return "N/A"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string.

    Args:
        bytes_value: Size in bytes

    Returns:
        Formatted size string (e.g., "1.5 GB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def calculate_percentage_change(
    current: float, previous: float
) -> float:
    """
    Calculate percentage change between two values.

    Args:
        current: Current value
        previous: Previous value

    Returns:
        Percentage change (can be negative)
    """
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100.0


def filter_by_status(
    items: List[Dict[str, Any]], status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter items by status field.

    Args:
        items: List of items to filter
        status: Status to filter by (None returns all)

    Returns:
        Filtered list of items
    """
    if status is None:
        return items
    return [item for item in items if item.get("status") == status]


def summarize_list(
    items: List[Dict[str, Any]], max_items: int = 5
) -> str:
    """
    Create a summary of a list with truncation.

    Args:
        items: List of items to summarize
        max_items: Maximum items to show before truncating

    Returns:
        Formatted summary string
    """
    if not items:
        return "No items found."

    summary = []
    for i, item in enumerate(items[:max_items], 1):
        summary.append(f"{i}. {item}")

    if len(items) > max_items:
        summary.append(f"... and {len(items) - max_items} more")

    return "\n".join(summary)


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """
    Calculate basic statistics from a list of values.

    Args:
        values: List of numeric values

    Returns:
        Dictionary with min, max, avg, median
    """
    if not values:
        return {"min": 0, "max": 0, "avg": 0, "median": 0}

    sorted_values = sorted(values)
    count = len(sorted_values)

    min_val = sorted_values[0]
    max_val = sorted_values[-1]
    avg = sum(sorted_values) / count
    median = sorted_values[count // 2]

    return {"min": min_val, "max": max_val, "avg": avg, "median": median}
