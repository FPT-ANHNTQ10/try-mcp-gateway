"""Tests for tools."""

import pytest
from datetime import datetime, timezone

from src.data_loader import DataLoader
from src.tools import (
    InterfaceLogsTool,
    BatchLogsTool,
    ApplicationLogsTool,
    ServerPerformanceTool,
    ApplicationPerformanceTool,
    MonitorResultsCheckTool,
    MonitoringSummaryTool,
    TrendAnalysisTool,
)
from src.utils import ToolExecutionError, TimeRangeError


@pytest.fixture
def data_loader():
    """Create a DataLoader instance for testing."""
    return DataLoader(base_path="data")


@pytest.fixture
def interface_logs_tool(data_loader):
    """Create InterfaceLogsTool instance."""
    return InterfaceLogsTool(data_loader)


@pytest.fixture
def batch_logs_tool(data_loader):
    """Create BatchLogsTool instance."""
    return BatchLogsTool(data_loader)


@pytest.fixture
def app_logs_tool(data_loader):
    """Create ApplicationLogsTool instance."""
    return ApplicationLogsTool(data_loader)


@pytest.fixture
def server_perf_tool(data_loader):
    """Create ServerPerformanceTool instance."""
    return ServerPerformanceTool(data_loader)


@pytest.fixture
def app_perf_tool(data_loader):
    """Create ApplicationPerformanceTool instance."""
    return ApplicationPerformanceTool(data_loader)


@pytest.fixture
def monitor_check_tool(data_loader):
    """Create MonitorResultsCheckTool instance."""
    return MonitorResultsCheckTool(data_loader)


@pytest.fixture
def monitoring_summary_tool(data_loader):
    """Create MonitoringSummaryTool instance."""
    return MonitoringSummaryTool(data_loader)


@pytest.fixture
def trend_analysis_tool(data_loader):
    """Create TrendAnalysisTool instance."""
    return TrendAnalysisTool(data_loader)


class TestInterfaceLogsTool:
    """Test InterfaceLogsTool."""

    @pytest.mark.asyncio
    async def test_execute_all_systems(self, interface_logs_tool):
        """Test fetching all interface logs."""
        result = await interface_logs_tool.execute(system_name="all", hours=24)
        assert isinstance(result, str)
        assert "Interface Logs Report" in result

    @pytest.mark.asyncio
    async def test_execute_specific_system(self, interface_logs_tool):
        """Test fetching logs for specific system."""
        result = await interface_logs_tool.execute(system_name="HR", hours=24)
        assert isinstance(result, str)
        assert "Interface Logs Report" in result

    @pytest.mark.asyncio
    async def test_execute_with_status_filter(self, interface_logs_tool):
        """Test fetching logs with status filter."""
        result = await interface_logs_tool.execute(
            system_name="all", hours=24, status="SUCCESS"
        )
        assert isinstance(result, str)
        assert "SUCCESS" in result or "No interface logs" in result


class TestBatchLogsTool:
    """Test BatchLogsTool."""

    @pytest.mark.asyncio
    async def test_execute_all_jobs(self, batch_logs_tool):
        """Test fetching all batch jobs."""
        result = await batch_logs_tool.execute(job_name="all", hours=24)
        assert isinstance(result, str)
        assert "Batch Jobs Report" in result

    @pytest.mark.asyncio
    async def test_execute_specific_job(self, batch_logs_tool):
        """Test fetching specific batch job."""
        result = await batch_logs_tool.execute(
            job_name="Premium Calculation", hours=24
        )
        assert isinstance(result, str)
        assert "Batch Jobs Report" in result


class TestApplicationLogsTool:
    """Test ApplicationLogsTool."""

    @pytest.mark.asyncio
    async def test_execute_all_services(self, app_logs_tool):
        """Test fetching all application logs."""
        result = await app_logs_tool.execute(service="all", minutes=60)
        assert isinstance(result, str)
        assert "Application Logs Report" in result

    @pytest.mark.asyncio
    async def test_execute_error_level(self, app_logs_tool):
        """Test fetching error level logs."""
        result = await app_logs_tool.execute(
            service="all", minutes=60, level="ERROR"
        )
        assert isinstance(result, str)
        assert "Application Logs Report" in result


class TestServerPerformanceTool:
    """Test ServerPerformanceTool."""

    @pytest.mark.asyncio
    async def test_execute_all_nodes(self, server_perf_tool):
        """Test fetching metrics for all nodes."""
        result = await server_perf_tool.execute(node="all", metric_type="all")
        assert isinstance(result, str)
        assert "Server Performance Report" in result

    @pytest.mark.asyncio
    async def test_execute_cpu_metric(self, server_perf_tool):
        """Test fetching CPU metrics."""
        result = await server_perf_tool.execute(node="all", metric_type="cpu")
        assert isinstance(result, str)
        assert "Server Performance Report" in result


class TestApplicationPerformanceTool:
    """Test ApplicationPerformanceTool."""

    @pytest.mark.asyncio
    async def test_execute_all_services(self, app_perf_tool):
        """Test fetching all service metrics."""
        result = await app_perf_tool.execute(service="all")
        assert isinstance(result, str)
        assert "Application Performance Report" in result

    @pytest.mark.asyncio
    async def test_execute_specific_service(self, app_perf_tool):
        """Test fetching specific service metrics."""
        result = await app_perf_tool.execute(service="api-gateway")
        assert isinstance(result, str)
        assert "Application Performance Report" in result


class TestMonitorResultsCheckTool:
    """Test MonitorResultsCheckTool."""

    @pytest.mark.asyncio
    async def test_execute_health_check(self, monitor_check_tool):
        """Test comprehensive health check."""
        result = await monitor_check_tool.execute()
        assert isinstance(result, str)
        assert "Monitor Results Check" in result
        assert "Interface Logs" in result
        assert "Batch Jobs" in result


class TestMonitoringSummaryTool:
    """Test MonitoringSummaryTool."""

    @pytest.mark.asyncio
    async def test_execute_summary(self, monitoring_summary_tool):
        """Test monitoring summary."""
        result = await monitoring_summary_tool.execute(time_range_hours=24)
        assert isinstance(result, str)
        assert "Monitoring Summary" in result


class TestTrendAnalysisTool:
    """Test TrendAnalysisTool."""

    @pytest.mark.asyncio
    async def test_analyze_cpu_trends(self, trend_analysis_tool):
        """Test CPU trend analysis."""
        result = await trend_analysis_tool.execute(
            metric="cpu", current_hours=1, comparison_hours=24
        )
        assert isinstance(result, str)
        assert "Trend Analysis" in result

    @pytest.mark.asyncio
    async def test_analyze_memory_trends(self, trend_analysis_tool):
        """Test memory trend analysis."""
        result = await trend_analysis_tool.execute(
            metric="memory", current_hours=1, comparison_hours=24
        )
        assert isinstance(result, str)
        assert "Trend Analysis" in result
