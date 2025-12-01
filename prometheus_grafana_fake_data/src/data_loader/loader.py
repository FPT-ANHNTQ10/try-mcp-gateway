"""Data loader utilities for loading YAML files."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..utils import DataLoadError, logger


class DataLoader:
    """Loader for YAML data files."""

    def __init__(self, base_path: str = "data"):
        """
        Initialize data loader.

        Args:
            base_path: Base path for data files
        """
        self.base_path = Path(base_path)
        self._cache: Dict[str, Any] = {}

    def load_yaml(
        self, filepath: str, use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Load YAML file.

        Args:
            filepath: Path to YAML file
            use_cache: Whether to use cached data

        Returns:
            Parsed YAML data as dictionary

        Raises:
            DataLoadError: If file cannot be loaded or parsed
        """
        full_path = self.base_path / filepath

        # Check cache first
        if use_cache and filepath in self._cache:
            logger.debug(f"Using cached data for {filepath}")
            return self._cache[filepath]

        try:
            if not full_path.exists():
                raise DataLoadError(f"File not found: {full_path}")

            with open(full_path, "r") as f:
                data = yaml.safe_load(f)
                logger.debug(f"Loaded data from {filepath}")

            # Cache the data
            self._cache[filepath] = data or {}
            return self._cache[filepath]

        except yaml.YAMLError as e:
            raise DataLoadError(f"Failed to parse YAML file {filepath}: {e}") from e
        except IOError as e:
            raise DataLoadError(f"Failed to read file {filepath}: {e}") from e

    def load_prometheus_metrics(self) -> Dict[str, Any]:
        """Load Prometheus metrics data."""
        return self.load_yaml("prometheus/metrics.yaml")

    def load_prometheus_alerts(self) -> Dict[str, Any]:
        """Load Prometheus alerts data."""
        return self.load_yaml("prometheus/alerts.yaml")

    def load_prometheus_targets(self) -> Dict[str, Any]:
        """Load Prometheus targets data."""
        return self.load_yaml("prometheus/targets.yaml")

    def load_interface_logs(self) -> Dict[str, Any]:
        """Load interface logs data."""
        return self.load_yaml("logs/interface_logs.yaml")

    def load_batch_logs(self) -> Dict[str, Any]:
        """Load batch logs data."""
        return self.load_yaml("logs/batch_logs.yaml")

    def load_application_logs(self) -> Dict[str, Any]:
        """Load application logs data."""
        return self.load_yaml("logs/application_logs.yaml")

    def load_server_metrics(self) -> Dict[str, Any]:
        """Load server performance metrics data."""
        return self.load_yaml("performance/server_metrics.yaml")

    def load_apm_data(self) -> Dict[str, Any]:
        """Load APM data."""
        return self.load_yaml("performance/apm_data.yaml")

    def load_grafana_dashboards(self) -> Dict[str, Any]:
        """Load Grafana dashboards data."""
        return self.load_yaml("grafana/dashboards.yaml")

    def load_grafana_datasources(self) -> Dict[str, Any]:
        """Load Grafana datasources data."""
        return self.load_yaml("grafana/datasources.yaml")

    def load_appl_area_metrics(self) -> Dict[str, Any]:
        """Load application area performance metrics data."""
        return self.load_yaml("performance/appl_area_metrics.yaml")

    def load_apm_traces(self) -> Dict[str, Any]:
        """Load APM distributed tracing data."""
        return self.load_yaml("apm/traces.yaml")

    def load_apm_metrics(self) -> Dict[str, Any]:
        """Load APM metrics data."""
        return self.load_yaml("apm/metrics.yaml")

    def load_health_check_data(self) -> Dict[str, Any]:
        """Load HTTP API health check endpoint data."""
        return self.load_yaml("health_checks/api_endpoints.yaml")

    def clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
        logger.debug("Cleared data cache")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_items": len(self._cache),
            "cache_keys": list(self._cache.keys()),
        }
