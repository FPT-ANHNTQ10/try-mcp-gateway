"""HTTP API Health Check tool - Prometheus format output."""

import json
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from ..data_loader import DataLoader
from ..utils import FilterError, TimeRangeError, ToolExecutionError, helpers
from .base import BaseTool


class ApiHealthCheckTool(BaseTool):
    """Tool for checking HTTP API health status - returns Prometheus API format."""

    async def execute(
        self,
        service_name: str = "all",
    ) -> str:
        """
        Check HTTP API health by calling health check endpoints.

        Args:
            service_name: Service name (e.g., "payment-service", "all")

        Returns:
            JSON string matching Prometheus API response format with health metrics

        Examples:
            - "Check health of payment service"
            - "Show me all API health status"
            - "Get health status for order service"

        Raises:
            ToolExecutionError: If execution fails
        """
        try:
            self._log_execution(service_name=service_name)

            # Load health check data
            data = self.data_loader.load_health_check_data()
            endpoints = data.get("health_check_endpoints", [])

            # Always return all checks regardless of filters
            filtered_checks = []
            for endpoint in endpoints:
                checks = endpoint.get("checks", [])
                for check in checks:
                    # Add endpoint metadata to check
                    filtered_checks.append({
                        "endpoint_id": endpoint.get("endpoint_id", "unknown"),
                        "url": endpoint.get("url", ""),
                        "name": endpoint.get("name", ""),
                        "service": endpoint.get("service", "unknown"),
                        "environment": endpoint.get("environment", "production"),
                        "region": endpoint.get("region", "unknown"),
                        "method": endpoint.get("method", "GET"),
                        "expected_status_code": endpoint.get("expected_status_code", 200),
                        **check
                    })

            # Current timestamp for Prometheus response
            current_timestamp = int(time.time())

            # Build Prometheus vector response
            result = []

            for check in filtered_checks:
                service_name = check.get("service", "unknown")
                endpoint_url = check.get("url", "")
                region = check.get("region", "unknown")
                environment = check.get("environment", "production")
                status = check.get("status", "UNKNOWN")
                status_code = check.get("status_code", 0)
                response_time_ms = check.get("response_time_ms", 0)
                expected_code = check.get("expected_status_code", 200)

                # Health status metric (1=UP, 0=DOWN/ERROR)
                health_up = 1 if status == "UP" else 0
                result.append({
                    "metric": {
                        "__name__": "api_health_up",
                        "service": service_name,
                        "url": endpoint_url,
                        "region": region,
                        "environment": environment
                    },
                    "value": [current_timestamp, str(health_up)]
                })

                # HTTP status code metric
                result.append({
                    "metric": {
                        "__name__": "api_health_status_code",
                        "service": service_name,
                        "url": endpoint_url,
                        "region": region
                    },
                    "value": [current_timestamp, str(status_code)]
                })

                # Response time metric
                result.append({
                    "metric": {
                        "__name__": "api_health_response_time_ms",
                        "service": service_name,
                        "url": endpoint_url,
                        "region": region
                    },
                    "value": [current_timestamp, str(response_time_ms)]
                })

                # Status match metric (1=matches expected, 0=doesn't match)
                status_match = 1 if status_code == expected_code else 0
                result.append({
                    "metric": {
                        "__name__": "api_health_status_code_match",
                        "service": service_name,
                        "url": endpoint_url,
                        "expected_code": str(expected_code)
                    },
                    "value": [current_timestamp, str(status_match)]
                })

                # Status label metric (for categorization)
                status_labels = {
                    "UP": 1,
                    "DOWN": 0,
                    "DEGRADED": 0.5,
                    "RATE_LIMITED": 0.3,
                    "ENDPOINT_NOT_FOUND": 0
                }
                status_value = status_labels.get(status, 0)
                result.append({
                    "metric": {
                        "__name__": "api_health_status",
                        "service": service_name,
                        "url": endpoint_url,
                        "status": status
                    },
                    "value": [current_timestamp, str(status_value)]
                })

                # Response time threshold check (slow response > 1000ms)
                slow_response = 1 if response_time_ms > 1000 else 0
                result.append({
                    "metric": {
                        "__name__": "api_health_slow_response",
                        "service": service_name,
                        "url": endpoint_url,
                        "threshold_ms": "1000"
                    },
                    "value": [current_timestamp, str(slow_response)]
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
            raise ToolExecutionError(f"Failed to check API health: {e}") from e
