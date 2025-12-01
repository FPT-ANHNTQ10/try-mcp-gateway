"""Interface logs tool - Database format output."""

import json
from datetime import datetime, timezone
from typing import Any, Optional

from ..data_loader import DataLoader
from ..utils import FilterError, TimeRangeError, ToolExecutionError, helpers
from .base import BaseTool


class InterfaceLogsTool(BaseTool):
    """Tool for checking interface logs - returns raw database query format."""

    async def execute(
        self,
        system_name: str = "all",
        hours: int = 1,
        status: Optional[str] = None,
    ) -> str:
        """
        Check interface logs for deployment abnormalities.

        Args:
            system_name: System to check (HR, Policy, Payment, or 'all')
            hours: Look back N hours from now
            status: Filter by status (SUCCESS, PENDING, ERROR, or None for all)

        Returns:
            JSON string matching database query response format

        Raises:
            ToolExecutionError: If execution fails
        """
        try:
            self._log_execution(system_name=system_name, hours=hours, status=status)

            # Validate inputs
            if hours < 0:
                raise TimeRangeError("Hours must be non-negative")

            # Load interface logs
            data = self.data_loader.load_interface_logs()
            logs = data.get("interface_logs", [])

            # Always return all logs regardless of filters
            filtered_logs = logs

            # Build SQL query representation (showing all data)
            query = "SELECT * FROM interface_logs ORDER BY timestamp DESC"

            # Build rows in database format
            rows = []
            for log in filtered_logs:
                row = {
                    "log_id": log.get("id", "unknown"),
                    "timestamp": log.get("created_at") or log.get("started_at"),
                    "system_name": log.get("system_name", "unknown"),
                    "interface_name": log.get("interface_name", "unknown"),
                    "direction": log.get("direction", "OUTBOUND"),
                    "status": log.get("status", "UNKNOWN"),
                    "protocol": log.get("protocol", "REST"),
                    "source_system": log.get("source_system", "unknown"),
                    "target_system": log.get("target_system", "unknown"),
                    "record_count": log.get("record_count", 0),
                    "bytes_transferred": log.get("bytes_transferred", 0),
                    "duration_seconds": log.get("duration_seconds", 0),
                    "retry_count": log.get("retry_count", 0),
                    "error_message": log.get("error_message"),
                    "correlation_id": log.get("correlation_id"),
                    "trace_id": log.get("trace_id")
                }
                rows.append(row)

            # Build response in database query result format
            response = {
                "query": query,
                "rowCount": len(rows),
                "rows": rows
            }

            return json.dumps(response, indent=2)

        except TimeRangeError:
            raise
        except FilterError:
            raise
        except Exception as e:
            raise ToolExecutionError(f"Failed to check interface logs: {e}") from e
