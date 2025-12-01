"""Application Performance Inquiry tool - Prometheus format output."""

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from ..data_loader import DataLoader
from ..utils import FilterError, TimeRangeError, ToolExecutionError, helpers
from .base import BaseTool


class ApplicationPerformanceInquiryTool(BaseTool):
    """Tool for monitoring APPL area performance - returns Prometheus API format."""

    async def execute(
        self,
        area: str = "all",
        time_range_minutes: int = 5,
    ) -> str:
        """
        Monitor the performance of the APPL (Application) area.

        Args:
            area: Application area to monitor (e.g., "payment", "order", "user", "all")
            time_range_minutes: Time range in minutes to query (default: 5)

        Returns:
            JSON string matching Prometheus API response format

        Raises:
            ToolExecutionError: If execution fails
        """
        try:
            self._log_execution(area=area, time_range_minutes=time_range_minutes)

            # Validate inputs
            if time_range_minutes < 0:
                raise TimeRangeError("Time range must be non-negative")

            # Load application area metrics
            data = self.data_loader.load_appl_area_metrics()
            application_areas = data.get("application_areas", {})

            # Always return all metrics regardless of filters
            filtered_metrics = []
            for area_name, area_data in application_areas.items():
                for metric in area_data.get("metrics", []):
                    # Add area info to metric
                    metric_with_area = {
                        "area": area_name,
                        "description": area_data.get("description", ""),
                        "criticality": area_data.get("criticality", "NORMAL"),
                        "sla_response_time_ms": area_data.get("sla_response_time_ms", 1000),
                        **metric
                    }
                    filtered_metrics.append(metric_with_area)

            # Current timestamp for Prometheus response
            current_timestamp = int(time.time())

            # Build Prometheus vector response
            result = []
            
            for metric in filtered_metrics:
                area_name = metric.get("area", "unknown")
                criticality = metric.get("criticality", "NORMAL")
                sla = metric.get("sla_response_time_ms", 1000)

                # Request rate metric
                result.append({
                    "metric": {
                        "__name__": "appl_area_request_rate",
                        "area": area_name,
                        "criticality": criticality
                    },
                    "value": [current_timestamp, str(metric.get("request_rate", 0))]
                })

                # Response time P50 metric
                result.append({
                    "metric": {
                        "__name__": "appl_area_response_time_ms",
                        "area": area_name,
                        "criticality": criticality,
                        "quantile": "0.50"
                    },
                    "value": [current_timestamp, str(metric.get("response_time_p50_ms", 0))]
                })

                # Response time P95 metric
                result.append({
                    "metric": {
                        "__name__": "appl_area_response_time_ms",
                        "area": area_name,
                        "criticality": criticality,
                        "quantile": "0.95"
                    },
                    "value": [current_timestamp, str(metric.get("response_time_p95_ms", 0))]
                })

                # Response time P99 metric
                result.append({
                    "metric": {
                        "__name__": "appl_area_response_time_ms",
                        "area": area_name,
                        "criticality": criticality,
                        "quantile": "0.99"
                    },
                    "value": [current_timestamp, str(metric.get("response_time_p99_ms", 0))]
                })

                # Error count metric
                result.append({
                    "metric": {
                        "__name__": "appl_area_error_count",
                        "area": area_name,
                        "criticality": criticality
                    },
                    "value": [current_timestamp, str(metric.get("error_count", 0))]
                })

                # Success count metric
                result.append({
                    "metric": {
                        "__name__": "appl_area_success_count",
                        "area": area_name,
                        "criticality": criticality
                    },
                    "value": [current_timestamp, str(metric.get("success_count", 0))]
                })

                # Throughput metric
                result.append({
                    "metric": {
                        "__name__": "appl_area_throughput_rps",
                        "area": area_name,
                        "criticality": criticality
                    },
                    "value": [current_timestamp, str(metric.get("throughput_rps", 0))]
                })

                # SLA compliance check (response time vs SLA)
                p95_time = metric.get("response_time_p95_ms", 0)
                sla_compliant = 1 if p95_time <= sla else 0
                result.append({
                    "metric": {
                        "__name__": "appl_area_sla_compliant",
                        "area": area_name,
                        "criticality": criticality,
                        "sla_ms": str(sla)
                    },
                    "value": [current_timestamp, str(sla_compliant)]
                })

            # Build Prometheus API response format
            response = {
                "status": "success",
                "data": {
                    "resultType": "vector",
                    "result": result
                }
            }

            return json.dumps(response, indent=2)

        except TimeRangeError:
            raise
        except FilterError:
            raise
        except Exception as e:
            raise ToolExecutionError(f"Failed to query application performance: {e}") from e
