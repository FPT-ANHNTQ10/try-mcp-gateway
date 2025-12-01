"""Tests for data loader."""

import pytest
from pathlib import Path

from src.data_loader import DataLoader
from src.utils import DataLoadError


@pytest.fixture
def data_loader():
    """Create a DataLoader instance for testing."""
    return DataLoader(base_path="data")


class TestDataLoader:
    """Test DataLoader functionality."""

    def test_load_prometheus_metrics(self, data_loader):
        """Test loading Prometheus metrics."""
        data = data_loader.load_prometheus_metrics()
        assert "metrics" in data
        assert len(data["metrics"]) > 0
        assert data["metrics"][0].get("name") is not None

    def test_load_interface_logs(self, data_loader):
        """Test loading interface logs."""
        data = data_loader.load_interface_logs()
        assert "interface_logs" in data
        assert len(data["interface_logs"]) > 0

    def test_load_batch_logs(self, data_loader):
        """Test loading batch logs."""
        data = data_loader.load_batch_logs()
        assert "batch_jobs" in data
        assert len(data["batch_jobs"]) > 0

    def test_load_application_logs(self, data_loader):
        """Test loading application logs."""
        data = data_loader.load_application_logs()
        assert "application_logs" in data
        assert len(data["application_logs"]) > 0

    def test_load_server_metrics(self, data_loader):
        """Test loading server metrics."""
        data = data_loader.load_server_metrics()
        assert "server_metrics" in data
        assert len(data["server_metrics"]) > 0

    def test_cache_functionality(self, data_loader):
        """Test caching mechanism."""
        # Load data twice
        data1 = data_loader.load_interface_logs()
        data2 = data_loader.load_interface_logs()

        # Should be same data
        assert data1 == data2

        # Check cache stats
        stats = data_loader.get_cache_stats()
        assert stats["cached_items"] >= 1

    def test_clear_cache(self, data_loader):
        """Test cache clearing."""
        # Load data
        data_loader.load_interface_logs()
        stats_before = data_loader.get_cache_stats()
        assert stats_before["cached_items"] > 0

        # Clear cache
        data_loader.clear_cache()
        stats_after = data_loader.get_cache_stats()
        assert stats_after["cached_items"] == 0

    def test_disable_cache(self, data_loader):
        """Test loading without cache."""
        data1 = data_loader.load_interface_logs(use_cache=False)
        data2 = data_loader.load_interface_logs(use_cache=False)

        # Both should have data
        assert data1 is not None
        assert data2 is not None


class TestDataLoaderErrors:
    """Test DataLoader error handling."""

    def test_invalid_file(self, data_loader):
        """Test loading non-existent file."""
        with pytest.raises(DataLoadError):
            data_loader.load_yaml("nonexistent/file.yaml")

    def test_malformed_yaml(self, tmp_path):
        """Test loading malformed YAML."""
        # Create a temporary malformed YAML file
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("invalid: yaml: syntax: here:")

        loader = DataLoader(base_path=str(tmp_path))
        with pytest.raises(DataLoadError):
            loader.load_yaml("test.yaml")
