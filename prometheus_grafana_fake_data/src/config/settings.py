"""Configuration settings loader for the monitoring MCP server."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ..utils import ConfigurationError, logger


class Settings:
    """Configuration settings manager."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize settings from config file.

        Args:
            config_path: Path to config.yaml file. If None, uses default locations.

        Raises:
            ConfigurationError: If config file cannot be loaded
        """
        self.config_path = self._find_config(config_path)
        self.config = self._load_config()
        self._initialize_defaults()

    @staticmethod
    def _find_config(config_path: Optional[str] = None) -> str:
        """
        Find config file in standard locations.

        Args:
            config_path: Explicit config path if provided

        Returns:
            Path to config file
        """
        if config_path and Path(config_path).exists():
            return config_path

        # Check standard locations
        locations = [
            "config.yaml",
            os.path.expanduser("~/.monitoring-mcp/config.yaml"),
            "/etc/monitoring-mcp/config.yaml",
        ]

        for location in locations:
            if Path(location).exists():
                return location

        # Fall back to example or return default
        if Path("config.yaml.example").exists():
            logger.warning("Using config.yaml.example as fallback")
            return "config.yaml.example"

        return "config.yaml"

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Returns:
            Configuration dictionary

        Raises:
            ConfigurationError: If file cannot be parsed
        """
        try:
            if not Path(self.config_path).exists():
                logger.warning(
                    f"Config file not found: {self.config_path}, using defaults"
                )
                return {}

            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
                return config or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML config: {e}") from e
        except IOError as e:
            raise ConfigurationError(f"Failed to read config file: {e}") from e

    def _initialize_defaults(self) -> None:
        """Set up default values for missing configuration."""
        if "server" not in self.config:
            self.config["server"] = {}
        if "data" not in self.config:
            self.config["data"] = {}
        if "time" not in self.config:
            self.config["time"] = {}
        if "thresholds" not in self.config:
            self.config["thresholds"] = {}

        # Set defaults
        self.config["server"].setdefault("name", "monitoring-mcp-server")
        self.config["server"].setdefault("version", "1.0.0")
        self.config["server"].setdefault("host", "0.0.0.0")
        self.config["server"].setdefault("port", 8000)
        self.config["server"].setdefault("transport", "stdio")
        self.config["server"].setdefault("log_level", "INFO")
        self.config["server"].setdefault("log_file", "logs/mcp_server.log")

        self.config["data"].setdefault("base_path", "data")
        self.config["data"].setdefault("prometheus_path", "data/prometheus")
        self.config["data"].setdefault("grafana_path", "data/grafana")
        self.config["data"].setdefault("logs_path", "data/logs")
        self.config["data"].setdefault("performance_path", "data/performance")

        self.config["time"].setdefault("timezone", "UTC")
        self.config["time"].setdefault("default_lookback_hours", 24)

        self.config["thresholds"].setdefault("cpu_warning", 70)
        self.config["thresholds"].setdefault("cpu_critical", 85)
        self.config["thresholds"].setdefault("memory_warning", 80)
        self.config["thresholds"].setdefault("memory_critical", 90)
        self.config["thresholds"].setdefault("error_rate_warning", 1.0)
        self.config["thresholds"].setdefault("error_rate_critical", 5.0)
        self.config["thresholds"].setdefault("latency_warning_ms", 500)
        self.config["thresholds"].setdefault("latency_critical_ms", 1000)

    def get(self, path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            path: Dot-separated path to config value (e.g., "server.name")
            default: Default value if path doesn't exist

        Returns:
            Configuration value or default
        """
        keys = path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    @property
    def server_name(self) -> str:
        """Get server name."""
        return self.get("server.name", "monitoring-mcp-server")

    @property
    def server_version(self) -> str:
        """Get server version."""
        return self.get("server.version", "1.0.0")

    @property
    def server_host(self) -> str:
        """Get server host."""
        return self.get("server.host", "0.0.0.0")

    @property
    def server_port(self) -> int:
        """Get server port."""
        return self.get("server.port", 8000)

    @property
    def server_transport(self) -> str:
        """Get server transport type (stdio, sse, streamable-http)."""
        return self.get("server.transport", "stdio")

    @property
    def log_level(self) -> str:
        """Get log level."""
        return self.get("server.log_level", "INFO")

    @property
    def log_file(self) -> str:
        """Get log file path."""
        return self.get("server.log_file", "logs/mcp_server.log")

    @property
    def prometheus_path(self) -> str:
        """Get Prometheus data path."""
        return self.get("data.prometheus_path", "data/prometheus")

    @property
    def grafana_path(self) -> str:
        """Get Grafana data path."""
        return self.get("data.grafana_path", "data/grafana")

    @property
    def logs_path(self) -> str:
        """Get logs data path."""
        return self.get("data.logs_path", "data/logs")

    @property
    def performance_path(self) -> str:
        """Get performance data path."""
        return self.get("data.performance_path", "data/performance")

    @property
    def timezone(self) -> str:
        """Get timezone."""
        return self.get("time.timezone", "UTC")

    @property
    def default_lookback_hours(self) -> int:
        """Get default lookback hours."""
        return self.get("time.default_lookback_hours", 24)

    @property
    def cpu_warning_threshold(self) -> float:
        """Get CPU warning threshold."""
        return self.get("thresholds.cpu_warning", 70)

    @property
    def cpu_critical_threshold(self) -> float:
        """Get CPU critical threshold."""
        return self.get("thresholds.cpu_critical", 85)

    @property
    def memory_warning_threshold(self) -> float:
        """Get memory warning threshold."""
        return self.get("thresholds.memory_warning", 80)

    @property
    def memory_critical_threshold(self) -> float:
        """Get memory critical threshold."""
        return self.get("thresholds.memory_critical", 90)

    @property
    def error_rate_warning_threshold(self) -> float:
        """Get error rate warning threshold."""
        return self.get("thresholds.error_rate_warning", 1.0)

    @property
    def error_rate_critical_threshold(self) -> float:
        """Get error rate critical threshold."""
        return self.get("thresholds.error_rate_critical", 5.0)

    @property
    def latency_warning_threshold_ms(self) -> float:
        """Get latency warning threshold in ms."""
        return self.get("thresholds.latency_warning_ms", 500)

    @property
    def latency_critical_threshold_ms(self) -> float:
        """Get latency critical threshold in ms."""
        return self.get("thresholds.latency_critical_ms", 1000)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings(config_path: Optional[str] = None) -> Settings:
    """
    Get or create global settings instance.

    Args:
        config_path: Path to config file

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings(config_path)
    return _settings
