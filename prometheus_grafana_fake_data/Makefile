.PHONY: help install dev test lint format build run clean

help:
	@echo "Monitoring MCP Server - Available Commands"
	@echo "=========================================="
	@echo "  make install    - Install dependencies using UV"
	@echo "  make dev        - Run in development mode"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"
	@echo "  make build      - Build Docker image"
	@echo "  make run        - Run Docker container"
	@echo "  make clean      - Clean build artifacts"
	@echo ""
	@echo "Examples:"
	@echo "  make install && make dev"
	@echo "  make test"
	@echo "  make build && make run"

install:
	uv sync

dev:
	uv run python -m src.servers.mcp_server

test:
	uv run pytest tests/ -v --tb=short

test-coverage:
	uv run pytest tests/ -v --cov=src --cov-report=html

lint:
	uv run ruff check src/ tests/

format:
	uv run ruff format src/ tests/

build:
	docker build -f Dockerfile.prod -t monitoring-mcp-server:latest .

build-dev:
	docker build -f Dockerfile -t monitoring-mcp-server:dev .

run:
	docker run --rm -p 8080:8080 -v "$$(pwd)/config.yaml:/app/config.yaml" monitoring-mcp-server:latest

run-dev:
	docker run --rm -it -p 8080:8080 -v "$$(pwd)/config.yaml:/app/config.yaml" monitoring-mcp-server:dev

run-stdio:
	docker run --rm -i -v "$$(pwd)/config.yaml:/app/config.yaml" monitoring-mcp-server:latest

run-http:
	@echo "Starting server with HTTP transport on port 8080..."
	docker run --rm -p 8080:8080 -v "$$(pwd)/config.yaml:/app/config.yaml" -e MCP_TRANSPORT=http monitoring-mcp-server:latest

clean:
	rm -rf .pytest_cache __pycache__ **/__pycache__ *.pyc **/*.pyc
	rm -rf .ruff_cache
	rm -rf logs/*.log
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

.DEFAULT_GOAL := help
