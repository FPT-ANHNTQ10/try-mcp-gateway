# Multi-stage Dockerfile for first_try_mcp
# Enterprise MCP Server with optimized build process using UV

# ============================================
# Stage 1: Builder
# ============================================
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim as builder

# Set working directory
WORKDIR /app

# Copy dependency files and README (required by pyproject.toml)
COPY pyproject.toml uv.lock README.md ./

# Copy source code (needed for editable install)
COPY src/ ./src/

# Install dependencies using UV
# UV automatically creates a virtual environment at /app/.venv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN uv sync --frozen --no-dev

# ============================================
# Stage 2: Runtime
# ============================================
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment and source from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY src/ ./src/
COPY config.yaml.example ./config.yaml.example
COPY README.md ./

# Create necessary directories
RUN mkdir -p logs && \
    chmod 755 logs

# Copy or create config file
# If config.yaml exists, copy it; otherwise use example
COPY config.yaml* ./
RUN if [ ! -f config.yaml ]; then cp config.yaml.example config.yaml; fi

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Switch to non-root user
USER mcpuser

# Expose port
EXPOSE 8000

# No health check - MCP server doesn't provide a standard health endpoint
# The server is healthy if it's running and accepting connections on port 8000

# Default command - run the MCP server
CMD ["python", "-m", "src.servers.http_server"]
