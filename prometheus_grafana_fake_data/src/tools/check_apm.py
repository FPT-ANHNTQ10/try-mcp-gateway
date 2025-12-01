"""Check APM tool - OpenTelemetry/Jaeger and Prometheus format output."""

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from ..data_loader import DataLoader
from ..utils import FilterError, TimeRangeError, ToolExecutionError, helpers
from .base import BaseTool


class CheckAPMTool(BaseTool):
    """Tool for querying APM data - returns OpenTelemetry/Jaeger or Prometheus format."""

    async def execute(
        self,
        service: str = "all",
        metric_type: str = "traces",
        minutes: int = 15,
        error_threshold: Optional[float] = None,
    ) -> str:
        """
        Query APM data such as application traces, error rates, and latency metrics.

        Args:
            service: Service name to query (e.g., "payment-service", "api-gateway", "all")
            metric_type: Type of APM data ("traces", "errors", "latency", "all")
            minutes: Time range in minutes (default: 15)
            error_threshold: Optional error rate threshold to filter (e.g., 5.0 for 5%)

        Returns:
            JSON string matching OpenTelemetry/Jaeger trace format or Prometheus metrics format

        Raises:
            ToolExecutionError: If execution fails
        """
        try:
            self._log_execution(
                service=service,
                metric_type=metric_type,
                minutes=minutes,
                error_threshold=error_threshold
            )

            # Validate inputs
            if minutes < 0:
                raise TimeRangeError("Minutes must be non-negative")

            valid_types = ["traces", "errors", "latency", "all"]
            if metric_type not in valid_types:
                raise FilterError(f"Invalid metric_type. Must be one of: {valid_types}")

            # Get time range
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(minutes=minutes)
            current_timestamp = int(time.time())

            response = {}

            # Load and process traces if requested
            if metric_type in ["traces", "all"]:
                traces_data = self.data_loader.load_apm_traces()
                traces_response = self._build_traces_response(
                    traces_data.get("traces", []),
                    service,
                    start_time,
                    end_time
                )
                if metric_type == "traces":
                    return json.dumps(traces_response, indent=2)
                response["traces"] = traces_response

            # Load and process metrics if requested
            if metric_type in ["errors", "latency", "all"]:
                metrics_data = self.data_loader.load_apm_metrics()
                metrics_response = self._build_metrics_response(
                    metrics_data.get("apm_metrics", []),
                    service,
                    metric_type,
                    start_time,
                    end_time,
                    current_timestamp,
                    error_threshold
                )
                if metric_type in ["errors", "latency"]:
                    return json.dumps(metrics_response, indent=2)
                response["metrics"] = metrics_response

            return json.dumps(response, indent=2)

        except TimeRangeError:
            raise
        except FilterError:
            raise
        except Exception as e:
            raise ToolExecutionError(f"Failed to query APM data: {e}") from e

    def _build_traces_response(
        self,
        traces: list,
        service: str,
        start_time: datetime,
        end_time: datetime
    ) -> dict:
        """Build OpenTelemetry/Jaeger style traces response."""
        # Always return all traces regardless of filters
        filtered_traces = []

        for trace in traces:

            # Build Jaeger-style trace format
            trace_id = trace.get("trace_id", "")
            spans = []
            processes = {}
            process_counter = 1

            for span in trace.get("spans", []):
                service_name = span.get("service_name", "unknown")
                
                # Create process reference
                process_key = f"p{process_counter}"
                if service_name not in [p.get("serviceName") for p in processes.values()]:
                    processes[process_key] = {
                        "serviceName": service_name,
                        "tags": {
                            "hostname": f"{service_name.replace('-', '_')}-pod-{trace_id[:8]}",
                            "ip": f"10.0.1.{process_counter + 10}"
                        }
                    }
                    process_counter += 1

                # Convert timestamp to microseconds
                span_start_str = span.get("start_time", "")
                start_time_us = 0
                if span_start_str:
                    try:
                        span_start = datetime.fromisoformat(span_start_str.replace("Z", "+00:00"))
                        start_time_us = int(span_start.timestamp() * 1_000_000)
                    except (ValueError, TypeError):
                        pass

                # Duration in microseconds
                duration_us = int(span.get("duration_ms", 0) * 1000)

                # Build span
                jaeger_span = {
                    "traceID": trace_id,
                    "spanID": span.get("span_id", ""),
                    "operationName": span.get("operation_name", ""),
                    "startTime": start_time_us,
                    "duration": duration_us,
                    "tags": span.get("tags", {}),
                    "logs": span.get("logs", [])
                }

                if span.get("parent_span_id"):
                    jaeger_span["parentSpanID"] = span["parent_span_id"]

                spans.append(jaeger_span)

            filtered_traces.append({
                "traceID": trace_id,
                "spans": spans,
                "processes": processes
            })

        return {"data": filtered_traces}

    def _build_metrics_response(
        self,
        metrics: list,
        service: str,
        metric_type: str,
        start_time: datetime,
        end_time: datetime,
        current_timestamp: int,
        error_threshold: Optional[float]
    ) -> dict:
        """Build Prometheus style metrics response."""
        result = []

        # Always return all metrics regardless of filters
        for metric in metrics:
            service_name = metric.get("service", "unknown")
            operation = metric.get("operation", "unknown")
            metrics_data = metric.get("metrics", {})
            error_rate = metrics_data.get("error_rate_percent", 0)

            # Add error-related metrics
            if metric_type in ["errors", "all"]:
                result.append({
                    "metric": {
                        "__name__": "apm_error_rate_percent",
                        "service": service_name,
                        "operation": operation
                    },
                    "value": [current_timestamp, str(error_rate)]
                })
                result.append({
                    "metric": {
                        "__name__": "apm_error_count",
                        "service": service_name,
                        "operation": operation
                    },
                    "value": [current_timestamp, str(metrics_data.get("error_count", 0))]
                })
                result.append({
                    "metric": {
                        "__name__": "apm_success_count",
                        "service": service_name,
                        "operation": operation
                    },
                    "value": [current_timestamp, str(metrics_data.get("success_count", 0))]
                })

            # Add latency-related metrics
            if metric_type in ["latency", "all"]:
                result.append({
                    "metric": {
                        "__name__": "apm_trace_duration_seconds",
                        "service": service_name,
                        "operation": operation,
                        "quantile": "0.50"
                    },
                    "value": [current_timestamp, str(metrics_data.get("trace_duration_p50_ms", 0) / 1000)]
                })
                result.append({
                    "metric": {
                        "__name__": "apm_trace_duration_seconds",
                        "service": service_name,
                        "operation": operation,
                        "quantile": "0.95"
                    },
                    "value": [current_timestamp, str(metrics_data.get("trace_duration_p95_ms", 0) / 1000)]
                })
                result.append({
                    "metric": {
                        "__name__": "apm_trace_duration_seconds",
                        "service": service_name,
                        "operation": operation,
                        "quantile": "0.99"
                    },
                    "value": [current_timestamp, str(metrics_data.get("trace_duration_p99_ms", 0) / 1000)]
                })
                result.append({
                    "metric": {
                        "__name__": "apm_request_rate",
                        "service": service_name,
                        "operation": operation
                    },
                    "value": [current_timestamp, str(metrics_data.get("request_rate_per_sec", 0))]
                })

        return {
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": result
            }
        }
