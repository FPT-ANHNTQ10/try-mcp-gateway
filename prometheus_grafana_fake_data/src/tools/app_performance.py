"""Application performance tool."""

from typing import Any, Optional

from ..data_loader import DataLoader
from ..utils import FilterError, TimeRangeError, ToolExecutionError, helpers
from .base import BaseTool


class ApplicationPerformanceTool(BaseTool):
    """Tool for viewing application performance metrics."""

    async def execute(
        self,
        service: str = "all",
        endpoint: Optional[str] = None,
        minutes: int = 5,
    ) -> str:
        """
        View application-level performance metrics (latency, throughput, error rates).

        Args:
            service: Service name or 'all'
            endpoint: Specific endpoint or None
            minutes: Time range in minutes

        Returns:
            Application performance metrics

        Raises:
            ToolExecutionError: If execution fails
        """
        try:
            self._log_execution(service=service, endpoint=endpoint, minutes=minutes)

            # Validate inputs
            if minutes < 0:
                raise TimeRangeError("Minutes must be non-negative")

            # Load APM data
            data = self.data_loader.load_apm_data()
            metrics = data.get("apm_metrics", [])

            # Always return all metrics regardless of filters
            filtered_metrics = metrics

            # Format results
            result_lines = []

            if not filtered_metrics:
                result_lines.append(
                    f"No APM metrics found for {service} in the last {minutes} minute(s)"
                )
            else:
                result_lines.append(
                    f"Found {len(filtered_metrics)} APM metric(s) for {service}:\n"
                )

                # Group by service
                services_dict: dict[str, list] = {}
                for metric in filtered_metrics:
                    svc = metric.get("service", "unknown")
                    if svc not in services_dict:
                        services_dict[svc] = []
                    services_dict[svc].append(metric)

                for svc, svc_metrics in services_dict.items():
                    items = []

                    for metric in svc_metrics:
                        # Handle nested metrics structure from YAML
                        nested_metrics = metric.get("metrics", {})
                        
                        endpoint_name = metric.get("operation", metric.get("endpoint", "N/A"))
                        # Map from new YAML field names to expected names
                        avg_latency = nested_metrics.get("trace_duration_p50_ms", metric.get("avg_latency_ms", 0))
                        p95_latency = nested_metrics.get("trace_duration_p95_ms", metric.get("p95_latency_ms", 0))
                        p99_latency = nested_metrics.get("trace_duration_p99_ms", metric.get("p99_latency_ms", 0))
                        error_rate = nested_metrics.get("error_rate_percent", metric.get("error_rate_percent", 0))
                        throughput = nested_metrics.get("request_rate_per_sec", metric.get("throughput_rps", 0))
                        request_count = nested_metrics.get("success_count", 0) + nested_metrics.get("error_count", 0)
                        if request_count == 0:
                            request_count = metric.get("request_count", 0)

                        # Status indicators
                        latency_status = "⚠️ " if avg_latency > 500 else "✓ "
                        error_status = "⚠️ " if error_rate > 1.0 else "✓ "

                        items.append(
                            f"Endpoint: {endpoint_name}\n"
                            f"    {latency_status}Latency: avg {avg_latency}ms, p95 {p95_latency}ms, p99 {p99_latency}ms\n"
                            f"    {error_status}Error Rate: {error_rate}%\n"
                            f"    Throughput: {throughput} req/s ({request_count} requests)"
                        )

                    result_lines.append(self._format_section(f"Service: {svc}", items))

            return self._format_result("Application Performance Report", "\n".join(result_lines))

        except (TimeRangeError, FilterError) as e:
            self._log_error(e)
            raise ToolExecutionError(f"Input validation failed: {str(e)}") from e
        except Exception as e:
            self._log_error(e)
            raise ToolExecutionError(
                f"Failed to view application performance: {str(e)}"
            ) from e
