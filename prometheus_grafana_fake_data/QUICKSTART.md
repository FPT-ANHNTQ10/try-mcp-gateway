# Quick Start Guide

Get up and running with the Monitoring MCP Server in 5 minutes!

## Prerequisites

- Python 3.11+
- UV package manager (or pip)

## Option 1: Local Development (Recommended)

### 1. Install Dependencies

```bash
cd promtheus_grafana_fake_data
make install
```

### 2. Run the Server

```bash
make dev
```

Expected output:

```
Starting monitoring-mcp-server v1.0.0
Log level: INFO
Data path: ...
Monitoring MCP server running and ready for connections
```

### 3. Test the Server

In another terminal:

```bash
# Run tests
make test

# Or with coverage
make test-coverage
```

## Option 2: Docker (Production-Like)

### 1. Build the Image

```bash
make build
```

### 2. Run the Container

```bash
make run
```

## Option 3: Quick Manual Testing

### 1. Install and Setup

```bash
cd promtheus_grafana_fake_data
uv sync
```

### 2. Run Python Directly

```bash
export PYTHONPATH=/home/ryan/Intern/first_try_mcp/mcp_gateway/promtheus_grafana_fake_data
uv run python -m src.servers.mcp_server
```

## Available Commands

```bash
make help          # Show all available commands
make install       # Install dependencies
make dev          # Run development server
make test         # Run tests
make lint         # Check code style
make format       # Format code
make build        # Build Docker image
make run          # Run Docker container
make clean        # Clean up build artifacts
```

## First MCP Tool Calls

Once the server is running, you can call these tools:

1. **Check Interface Logs**

   ```
   "Show me all interface logs for the HR system"
   ```

2. **Check Batch Jobs**

   ```
   "Show me all batch jobs from the last 24 hours"
   ```

3. **Check Application Logs**

   ```
   "Show me errors from the payment service in the last 30 minutes"
   ```

4. **View Server Performance**

   ```
   "Show CPU usage for all nodes"
   ```

5. **View App Performance**

   ```
   "Show me latency metrics for the API gateway"
   ```

6. **Monitor Health Check**

   ```
   "Run a full health check"
   ```

7. **View Summary**

   ```
   "Give me a summary of the last 24 hours"
   ```

8. **Analyze Trends**
   ```
   "Compare current CPU usage with 24 hours ago"
   ```

## Project Layout

```
promtheus_grafana_fake_data/
├── data/              # Fake data files
├── src/               # Source code
│   ├── config/        # Configuration management
│   ├── servers/       # MCP server
│   ├── tools/         # 8 MCP tools
│   ├── data_loader/   # YAML loading
│   └── utils/         # Utilities
├── tests/             # Test suite
├── Makefile           # Build commands
├── README.md          # Full documentation
└── config.yaml        # Configuration file
```

## Troubleshooting

### UV not found

```bash
pip install uv
# or
brew install uv  # on macOS
```

### Import errors

```bash
# Make sure you're in the project directory
cd promtheus_grafana_fake_data

# Set PYTHONPATH
export PYTHONPATH=$(pwd)

# Run again
make dev
```

### Port already in use

Change the server configuration in `config.yaml` or kill the existing process.

### Data files not found

Verify data files exist:

```bash
ls -la data/logs/
ls -la data/prometheus/
ls -la data/performance/
ls -la data/grafana/
```

## Next Steps

1. **Read the README.md** for comprehensive documentation
2. **Check PROJECT_COMPLETION.md** for implementation details
3. **Run the tests** to verify everything works
4. **Explore the source code** to understand the implementation
5. **Customize the fake data** in `data/` directory

## Performance Tips

- The server loads data into memory on first access
- Subsequent accesses use cached data (fast)
- Clear cache with `data_loader.clear_cache()` if needed
- Logs grow in `logs/mcp_server.log` - rotate as needed

## Support

- Check logs: `tail -f logs/mcp_server.log`
- Review README.md for detailed documentation
- Run tests: `make test`
- Check configuration: `cat config.yaml`

---

**You're all set!** 🎉

The Monitoring MCP Server is now ready for development and testing.
