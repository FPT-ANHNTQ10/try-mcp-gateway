FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Copy all files
COPY . .

# Install dependencies with dev packages (generates lock file if needed)
RUN uv sync

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Development mode
CMD ["python", "-m", "src.servers.mcp_server"]
