"""Application logs tool - Elasticsearch format output."""

import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from ..data_loader import DataLoader
from ..utils import FilterError, TimeRangeError, ToolExecutionError, helpers
from .base import BaseTool


class ApplicationLogsTool(BaseTool):
    """Tool for checking application logs - returns Elasticsearch response format."""

    async def execute(
        self,
        service: str = "all",
        minutes: int = 30,
        level: str = "ERROR",
        search_pattern: Optional[str] = None,
    ) -> str:
        try:
            self._log_execution(
                service=service, minutes=minutes, level=level, search_pattern=search_pattern
            )

            if minutes < 0:
                raise TimeRangeError("Minutes must be non-negative")

            valid_levels = ["DEBUG", "INFO", "WARN", "ERROR"]
            if level not in valid_levels:
                raise FilterError(f"Level must be one of {valid_levels}")

            data = self.data_loader.load_application_logs()
            logs = data.get("application_logs", [])

            # Always return all logs regardless of filters
            filtered_logs = logs

            hits = []
            today = datetime.now(timezone.utc).strftime("%Y.%m.%d")

            for log in filtered_logs:
                # Extract exception info from nested structure
                exception = log.get("exception", {})
                context = log.get("context", {})
                
                hit = {
                    "_index": f"app-logs-{today}",
                    "_id": str(uuid.uuid4())[:12],
                    "_score": None,
                    "_source": {
                        "@timestamp": log.get("timestamp", datetime.now(timezone.utc).isoformat()),
                        "level": log.get("level", "INFO"),
                        "logger_name": log.get("logger", f"com.company.{log.get('service', 'unknown')}.Service"),
                        "message": log.get("message", ""),
                        "thread_name": log.get("thread", f"http-nio-8080-exec-{hash(log.get('message', '')) % 50}"),
                        "service": log.get("service", "unknown"),
                        "instance": log.get("instance", f"{log.get('service', 'unknown')}-{uuid.uuid4().hex[:8]}"),
                        "namespace": log.get("namespace", "production"),
                        "version": log.get("version", "unknown"),
                        "trace_id": log.get("trace_id", uuid.uuid4().hex),
                        "span_id": log.get("span_id", uuid.uuid4().hex[:16]),
                        "parent_span_id": log.get("parent_span_id"),
                        "request_id": log.get("request_id")
                    }
                }

                # Add exception details for errors
                if log.get("level") == "ERROR" and exception:
                    hit["_source"]["exception_class"] = exception.get("class", "java.lang.Exception")
                    hit["_source"]["exception_message"] = exception.get("message", log.get("message", "Unknown error"))
                    hit["_source"]["stack_trace"] = exception.get("stacktrace", (
                        f"java.lang.Exception: {log.get('message', 'Unknown error')}\n"
                        "\tat com.company.service.Handler.process(Handler.java:123)\n"
                        "\tat com.company.service.Controller.handle(Controller.java:45)"
                    ))
                elif log.get("level") == "ERROR":
                    hit["_source"]["stack_trace"] = (
                        f"java.lang.Exception: {log.get('message', 'Unknown error')}\n"
                        "\tat com.company.service.Handler.process(Handler.java:123)\n"
                        "\tat com.company.service.Controller.handle(Controller.java:45)"
                    )

                # Add context fields if available
                if context:
                    hit["_source"]["context"] = context
                    if context.get("transaction_id"):
                        hit["_source"]["transaction_id"] = context.get("transaction_id")
                    if context.get("customer_id"):
                        hit["_source"]["customer_id"] = context.get("customer_id")

                if log.get("user_id"):
                    hit["_source"]["user_id"] = log.get("user_id")

                hits.append(hit)

            response = {
                "took": 5,
                "timed_out": False,
                "_shards": {
                    "total": 5,
                    "successful": 5,
                    "skipped": 0,
                    "failed": 0
                },
                "hits": {
                    "total": {
                        "value": len(hits),
                        "relation": "eq"
                    },
                    "max_score": None,
                    "hits": hits
                }
            }

            return json.dumps(response, indent=2, default=str)

        except (TimeRangeError, FilterError) as e:
            self._log_error(e)
            raise ToolExecutionError(f"Input validation failed: {str(e)}") from e
        except Exception as e:
            self._log_error(e)
            raise ToolExecutionError(f"Failed to check application logs: {str(e)}") from e
