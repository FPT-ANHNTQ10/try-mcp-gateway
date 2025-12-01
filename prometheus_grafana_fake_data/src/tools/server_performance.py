"""Server performance tool - Prometheus format output."""

import json
import time
from datetime import datetime, timezone
from typing import Any, Optional

from ..data_loader import DataLoader
from ..utils import FilterError, TimeRangeError, ToolExecutionError, helpers
from .base import BaseTool


class ServerPerformanceTool(BaseTool):
    """Tool for viewing server performance metrics - returns Prometheus API response format."""

    async def execute(
        self,
        node: str = "all",
        metric_type: str = "all",
        minutes: int = 5,
    ) -> str:
        try:
            self._log_execution(node=node, metric_type=metric_type, minutes=minutes)

            if minutes < 0:
                raise TimeRangeError("Minutes must be non-negative")

            valid_types = ["cpu", "memory", "disk_io", "network", "all"]
            if metric_type not in valid_types:
                raise FilterError(f"Metric type must be one of {valid_types}")

            data = self.data_loader.load_server_metrics()
            metrics = data.get("server_metrics", [])

            # Always return all metrics regardless of filters
            filtered_metrics = metrics

            current_timestamp = int(time.time())
            
            # Build Prometheus-style results for each metric type
            prometheus_results = {}

            if metric_type in ["cpu", "all"]:
                cpu_results = []
                for m in filtered_metrics:
                    cpu_results.append({
                        "metric": {
                            "__name__": "node_cpu_usage_percent",
                            "instance": f"{m.get('node', 'unknown')}:9100",
                            "job": "node-exporter",
                            "zone": m.get("zone", "us-east-1a")
                        },
                        "value": [current_timestamp, str(m.get("cpu_usage_percent", 0))]
                    })
                prometheus_results["cpu_usage"] = {
                    "query": "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
                    "response": {
                        "status": "success",
                        "data": {
                            "resultType": "vector",
                            "result": cpu_results
                        }
                    }
                }

            if metric_type in ["memory", "all"]:
                memory_results = []
                for m in filtered_metrics:
                    memory_results.append({
                        "metric": {
                            "__name__": "node_memory_usage_percent",
                            "instance": f"{m.get('node', 'unknown')}:9100",
                            "job": "node-exporter"
                        },
                        "value": [current_timestamp, str(m.get("memory_usage_percent", 0))]
                    })
                prometheus_results["memory_usage"] = {
                    "query": "100 * (1 - ((node_memory_MemAvailable_bytes) / (node_memory_MemTotal_bytes)))",
                    "response": {
                        "status": "success",
                        "data": {
                            "resultType": "vector",
                            "result": memory_results
                        }
                    }
                }

            if metric_type in ["disk_io", "all"]:
                disk_read_results = []
                disk_write_results = []
                for m in filtered_metrics:
                    disk_read_results.append({
                        "metric": {
                            "__name__": "node_disk_read_mbps",
                            "instance": f"{m.get('node', 'unknown')}:9100",
                            "device": "sda"
                        },
                        "value": [current_timestamp, str(m.get("disk_io_read_mbps", 0))]
                    })
                    disk_write_results.append({
                        "metric": {
                            "__name__": "node_disk_write_mbps",
                            "instance": f"{m.get('node', 'unknown')}:9100",
                            "device": "sda"
                        },
                        "value": [current_timestamp, str(m.get("disk_io_write_mbps", 0))]
                    })
                prometheus_results["disk_io"] = {
                    "query": "rate(node_disk_read_bytes_total[5m]) / 1024 / 1024",
                    "response": {
                        "status": "success",
                        "data": {
                            "resultType": "vector",
                            "result": disk_read_results + disk_write_results
                        }
                    }
                }

            if metric_type in ["network", "all"]:
                network_results = []
                for m in filtered_metrics:
                    network_results.append({
                        "metric": {
                            "__name__": "node_network_receive_mbps",
                            "instance": f"{m.get('node', 'unknown')}:9100",
                            "device": "eth0"
                        },
                        "value": [current_timestamp, str(m.get("network_rx_mbps", 0))]
                    })
                    network_results.append({
                        "metric": {
                            "__name__": "node_network_transmit_mbps",
                            "instance": f"{m.get('node', 'unknown')}:9100",
                            "device": "eth0"
                        },
                        "value": [current_timestamp, str(m.get("network_tx_mbps", 0))]
                    })
                prometheus_results["network"] = {
                    "query": "rate(node_network_receive_bytes_total[5m]) / 1024 / 1024",
                    "response": {
                        "status": "success",
                        "data": {
                            "resultType": "vector",
                            "result": network_results
                        }
                    }
                }

            response = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": "prometheus",
                "metrics": prometheus_results
            }

            return json.dumps(response, indent=2, default=str)

        except (TimeRangeError, FilterError) as e:
            self._log_error(e)
            raise ToolExecutionError(f"Input validation failed: {str(e)}") from e
        except Exception as e:
            self._log_error(e)
            raise ToolExecutionError(f"Failed to view server performance: {str(e)}") from e
