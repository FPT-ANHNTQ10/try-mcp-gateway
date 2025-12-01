# Monitoring MCP Server

A production-grade MCP (Model Context Protocol) server that simulates monitoring operations for Prometheus and Grafana with realistic fake data. This server provides comprehensive tools for querying monitoring data, analyzing trends, and checking system health.

## Features

- **8 Powerful MCP Tools** for comprehensive monitoring operations
- **Realistic Fake Data** closely resembling real-world monitoring scenarios
- **Time-based Filtering** to query data across different time ranges
- **Trend Analysis** to detect patterns and anomalies
- **Comprehensive Health Checks** across all monitoring dimensions
- **Production-Ready Docker Setup** with multi-stage builds
- **Extensive Logging** with structured logging support
- **Type-Safe** with full type hints and validation

## Quick Start

### Prerequisites

- Python 3.11+
- UV package manager (recommended) or pip
- Docker (optional, for containerized deployment)

### Installation

```bash
# Clone or navigate to the project
cd monitoring-mcp-server

# Install dependencies using UV
make install

# Or manually with uv
uv sync
```

### Running the Server

**Development Mode:**

```bash
make dev
# Or directly with uv
uv run python -m src.servers.mcp_server
```

**Docker (Development):**

```bash
make build-dev
make run-dev
```

**Docker (Production):**

```bash
make build
make run
```

## Configuration

The server uses a YAML configuration file. Copy the example and customize:

```bash
cp config.yaml.example config.yaml
```

### Configuration Options

```yaml
# MCP Server Configuration
server:
  name: "monitoring-mcp-server"
  version: "1.0.0"
  log_level: "INFO"
  log_file: "logs/mcp_server.log"

# Data paths
data:
  base_path: "data"
  prometheus_path: "data/prometheus"
  grafana_path: "data/grafana"
  logs_path: "data/logs"
  performance_path: "data/performance"

# Time settings
time:
  timezone: "UTC"
  default_lookback_hours: 24

# Alerting thresholds
thresholds:
  cpu_warning: 70
  cpu_critical: 85
  memory_warning: 80
  memory_critical: 90
  error_rate_warning: 1.0
  error_rate_critical: 5.0
  latency_warning_ms: 500
  latency_critical_ms: 1000
```

## Available MCP Tools

### 1. Check Interface Logs

Monitor interface/integration logs for data exchange operations.

**Parameters:**

- `system_name` (str): System to check (HR, Policy, Payment, Inventory, Finance, or 'all')
- `hours` (int): Look back N hours (default: 1)
- `status` (str, optional): Filter by status (SUCCESS, PENDING, ERROR)

**Examples:**

```
"Check today's interface data for the HR system"
"Show me I/F records that failed in the last 1 hour"
"Is there any I/F data stuck in PENDING status?"
```

### 2. Check Batch Logs

Monitor batch processing jobs for abnormalities and failures.

**Parameters:**

- `job_name` (str): Batch job name or 'all' (default: 'all')
- `hours` (int): Look back N hours (default: 24)
- `status` (str, optional): Filter by status (SUCCESS, FAILED, RUNNING)

**Examples:**

```
"Check the results of last night's batch jobs"
"Show me failed batch records for the premium calculation batch"
"Did the membership sync batch complete successfully today?"
```

### 3. Check Application Logs

Retrieve and analyze application logs for errors and exceptions.

**Parameters:**

- `service` (str): Service name or 'all' (default: 'all')
- `minutes` (int): Look back N minutes (default: 30)
- `level` (str): Log level - ERROR, WARN, INFO (default: 'ERROR')
- `search_pattern` (str, optional): Search for specific pattern in message

**Examples:**

```
"Search the application logs for errors in the last 30 minutes"
"Show me all WARN or ERROR logs for the payment service"
"Are there any database connection errors?"
```

### 4. View Server Performance

Check real-time server and infrastructure performance metrics.

**Parameters:**

- `node` (str): Node name or 'all' (default: 'all')
- `metric_type` (str): Type of metric - cpu, memory, disk_io, network, or 'all' (default: 'all')
- `minutes` (int): Time range in minutes (default: 5)

**Examples:**

```
"Show me CPU usage for all nodes"
"What's the memory usage on k8s-node-01?"
"Check network I/O across all nodes"
"Are any nodes running hot?"
```

### 5. View Application Performance

View application-level performance metrics (latency, throughput, error rates).

**Parameters:**

- `service` (str): Service name or 'all' (default: 'all')
- `endpoint` (str, optional): Specific endpoint
- `minutes` (int): Time range in minutes (default: 5)

**Examples:**

```
"Show me API latency for payment service"
"What's the error rate across all services?"
"Check throughput for the api-gateway"
"Is /api/v1/users experiencing high latency?"
```

### 6. Monitor Results Check

Validate the current health of all monitored items in a single request.

**Parameters:** None

**Examples:**

```
"Run a full health check"
"Check all monitoring results"
"What's the overall system health?"
```

### 7. View Monitoring Summary

Receive a high-level summary of all monitoring outputs.

**Parameters:**

- `time_range_hours` (int): Summary time range (default: 24)

**Examples:**

```
"Give me a monitoring summary for the last 24 hours"
"Show me an overview of system health"
"What happened in the monitoring data today?"
```

### 8. Analyze Trends

Compare current monitoring values with historical data to detect trends.

**Parameters:**

- `metric` (str): Metric to analyze - cpu, memory, latency, error_rate, throughput, disk_io, network
- `current_hours` (int): Current period duration (default: 1)
- `comparison_hours` (int): Historical period to compare against (default: 24)

**Examples:**

```
"Compare current CPU usage with yesterday"
"Analyze error rate trends over the past week"
"Is memory usage increasing?"
"How does latency compare to 24 hours ago?"
```

## Project Structure

```
monitoring-mcp-server/
├── config.yaml                    # Main configuration (gitignored)
├── config.yaml.example            # Example configuration template
├── Dockerfile                     # Development Docker build
├── Dockerfile.prod                # Production multi-stage Docker build
├── Makefile                       # Common commands
├── pyproject.toml                 # UV project configuration
├── README.md                      # This file
├── logs/
│   └── mcp_server.log            # Application logs
├── data/                          # Fake data storage
│   ├── prometheus/
│   │   ├── metrics.yaml          # Fake Prometheus metrics
│   │   ├── alerts.yaml           # Fake alert rules
│   │   └── targets.yaml          # Fake scrape targets
│   ├── grafana/
│   │   ├── dashboards.yaml       # Fake dashboard definitions
│   │   └── datasources.yaml      # Fake datasources
│   ├── logs/
│   │   ├── interface_logs.yaml   # Fake I/F logs
│   │   ├── batch_logs.yaml       # Fake batch job logs
│   │   └── application_logs.yaml # Fake application logs
│   └── performance/
│       ├── server_metrics.yaml   # Fake server performance data
│       └── apm_data.yaml          # Fake APM data
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Configuration loader
│   ├── servers/
│   │   ├── __init__.py
│   │   └── mcp_server.py          # Main FastMCP server
│   ├── tools/                     # MCP Tools implementation
│   │   ├── __init__.py
│   │   ├── base.py                # Base tool class
│   │   ├── interface_logs.py      # I/F logs tool
│   │   ├── batch_logs.py          # Batch logs tool
│   │   ├── application_logs.py    # App logs tool
│   │   ├── server_performance.py  # Server perf tool
│   │   ├── app_performance.py     # App perf tool
│   │   ├── monitor_check.py       # Monitor check tool
│   │   ├── monitor_summary.py     # Summary tool
│   │   └── trend_analysis.py      # Trend analysis tool
│   ├── data_loader/
│   │   ├── __init__.py
│   │   └── loader.py              # YAML data loader
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py          # Custom exceptions
│       ├── logger.py              # Logging setup
│       └── helpers.py             # Helper functions
└── tests/
    ├── __init__.py
    ├── test_tools.py              # Tool tests
    └── test_data_loader.py        # Data loader tests
```

## Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make test-coverage
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Both lint and format can be run together
make lint format
```

### Useful Commands

```bash
# Install dependencies
make install

# Run development server
make dev

# Build Docker images
make build          # Production build
make build-dev      # Development build

# Run Docker containers
make run            # Production container
make run-dev        # Development container

# Clean up
make clean
```

## Fake Data Overview

The project includes realistic fake data that mimics real-world monitoring scenarios:

### Interface Logs (`data/logs/interface_logs.yaml`)

- Multiple system integrations (HR, Policy, Payment, Inventory, Finance, Payroll)
- Varying statuses: SUCCESS, PENDING, ERROR
- Record counts and error messages
- Timestamp ranges throughout the past days

### Batch Jobs (`data/logs/batch_logs.yaml`)

- Various batch job types (Premium Calculation, Membership Sync, Reporting, etc.)
- Job execution durations and record counts
- Success and failure scenarios
- Running jobs for realistic monitoring

### Application Logs (`data/logs/application_logs.yaml`)

- Multiple services (payment-service, auth-service, api-gateway, database-service, etc.)
- Various log levels (ERROR, WARN, INFO)
- Error codes and trace IDs
- Realistic error messages and context

### Server Metrics (`data/performance/server_metrics.yaml`)

- Multiple Kubernetes nodes (k8s-node-01, k8s-node-02, k8s-node-03)
- CPU, memory, disk I/O, and network metrics
- Realistic usage patterns and threshold violations
- Time-series data across multiple nodes

### APM Data (`data/performance/apm_data.yaml`)

- Multiple services (api-gateway, payment-service, etc.)
- Endpoints with latency percentiles (avg, p95, p99)
- Error rates and throughput metrics
- Real-world performance characteristics

### Prometheus Metrics (`data/prometheus/metrics.yaml`)

- Node exporter metrics (CPU, memory, network)
- Container metrics
- Service availability indicators
- Time-series values with labels

## Docker Deployment

### Development Image

```bash
make build-dev
make run-dev
```

### Production Image (Multi-stage)

```bash
make build
make run
```

The production Dockerfile uses a multi-stage build to minimize image size:

1. **Builder stage**: Installs all dependencies
2. **Runtime stage**: Contains only runtime essentials

## Environment Variables

The server respects the following environment variables:

- `PYTHONPATH`: Set to `/app` in Docker images
- `PATH`: Includes the virtual environment bin directory

## Logging

Logs are written to both console and file:

- **Console**: All log levels (colored output)
- **File**: `logs/mcp_server.log`

Log level is configurable via `config.yaml`:

```yaml
server:
  log_level: "INFO" # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Troubleshooting

### Issues with UV

If UV is not installed:

```bash
pip install uv
# Or on macOS
brew install uv
```

### Configuration File Not Found

The server looks for `config.yaml` in:

1. Current directory
2. `~/.monitoring-mcp/config.yaml`
3. `/etc/monitoring-mcp/config.yaml`
4. Falls back to `config.yaml.example` with warnings

### Docker Build Failures

Make sure you're in the project root:

```bash
cd monitoring-mcp-server
make build
```

### Test Failures

Ensure data files exist and are properly formatted:

```bash
# Verify YAML files
python -c "import yaml; yaml.safe_load(open('data/logs/interface_logs.yaml'))"
```

## Performance Characteristics

- **Data Loading**: YAML files are cached in memory for fast access
- **Response Time**: Tools typically respond within milliseconds
- **Memory Usage**: Minimal footprint (~50MB for runtime)
- **Scalability**: Can handle thousands of fake monitoring records

## Security Considerations

- No external network calls (self-contained fake data)
- No authentication required for demo purposes
- Logs contain simulated data only
- Safe to run in any environment

## Future Enhancements

Potential improvements for production use:

- Real Prometheus/Grafana data integration
- WebSocket streaming for real-time updates
- Database backend for data persistence
- Advanced analytics and anomaly detection
- Multi-tenant support
- Distributed tracing integration

## Contributing

To extend the server:

1. **Add new tools**: Create new files in `src/tools/`
2. **Add new data**: Update YAML files in `data/`
3. **Extend configuration**: Modify `src/config/settings.py`
4. **Add tests**: Create tests in `tests/`

## License

This project is provided as-is for demonstration and testing purposes.

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review configuration examples
3. Check logs in `logs/mcp_server.log`
4. Verify data files are present and properly formatted

## Version History

- **v1.0.0** (2025-11-30): Initial production-ready release
  - 8 comprehensive MCP tools
  - Realistic fake data
  - Full Docker support
  - Comprehensive documentation
