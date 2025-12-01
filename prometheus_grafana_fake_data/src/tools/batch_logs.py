"""Batch logs tool - Database format output."""

import json
from datetime import datetime, timezone
from typing import Any, Optional

from ..data_loader import DataLoader
from ..utils import FilterError, TimeRangeError, ToolExecutionError, helpers
from .base import BaseTool


class BatchLogsTool(BaseTool):
    """Tool for checking batch job logs - returns raw database query format."""

    async def execute(
        self,
        job_name: str = "all",
        hours: int = 24,
        status: Optional[str] = None,
    ) -> str:
        """
        Check batch processing results for abnormalities.

        Args:
            job_name: Batch job name or 'all'
            hours: Look back N hours
            status: Filter by status (COMPLETED, FAILED, RUNNING, or None)

        Returns:
            JSON string matching database query response format

        Raises:
            ToolExecutionError: If execution fails
        """
        try:
            self._log_execution(job_name=job_name, hours=hours, status=status)

            # Validate inputs
            if hours < 0:
                raise TimeRangeError("Hours must be non-negative")

            # Load batch logs
            data = self.data_loader.load_batch_logs()
            jobs = data.get("batch_jobs", [])

            # Always return all jobs regardless of filters
            filtered_jobs = jobs

            # Build SQL query representation (showing all data)
            query = "SELECT * FROM batch_job_logs ORDER BY start_time DESC"

            # Build rows in database format
            rows = []
            for job in filtered_jobs:
                job_status = job.get("status", "UNKNOWN")
                row = {
                    "job_id": job.get("job_id", "unknown"),
                    "job_name": job.get("job_name", "unknown"),
                    "job_group": job.get("job_group", "DEFAULT"),
                    "job_type": job.get("job_type", "BATCH"),
                    "priority": job.get("priority", "NORMAL"),
                    "status": job_status,
                    "scheduled_time": job.get("scheduled_time"),
                    "start_time": job.get("start_time"),
                    "end_time": job.get("end_time"),
                    "duration_seconds": job.get("duration_seconds", 0),
                    "exit_code": 0 if job_status == "SUCCESS" else (1 if job_status == "FAILED" else None),
                    "records_processed": job.get("records_processed", 0),
                    "records_failed": job.get("records_failed", 0),
                    "retry_count": job.get("retry_count", 0),
                    "max_retries": job.get("max_retries", 3),
                    "run_as_user": job.get("run_as_user", "batch"),
                    "host": job.get("host", "batch-server-01"),
                    "correlation_id": job.get("correlation_id"),
                    "log_file": f"/var/log/batch/{job.get('job_id', 'unknown')}.log"
                }

                # Add resource usage if available
                resource_usage = job.get("resource_usage", {})
                if resource_usage:
                    row["cpu_percent_avg"] = resource_usage.get("cpu_percent_avg")
                    row["memory_mb_peak"] = resource_usage.get("memory_mb_peak")
                    row["disk_io_mb"] = resource_usage.get("disk_io_mb")

                # Add error_log for failed jobs
                if job_status == "FAILED":
                    row["error_log"] = job.get("error_message", "ERROR: Job execution failed\nDETAIL: See log file for details")

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
            raise ToolExecutionError(f"Failed to check batch logs: {e}") from e
