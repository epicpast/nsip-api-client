# NSIP MCP Server Dockerfile
# Multi-stage build for optimized image size and security
# Version: 1.1.0

# ============================================================================
# Stage 1: Builder - Install dependencies and compile wheels
# ============================================================================
FROM python:3.11-slim AS builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment for isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only dependency files first for better layer caching
COPY pyproject.toml /tmp/

# Install Python dependencies
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir build

# Copy source code
WORKDIR /build
COPY . .

# Build wheel
RUN python -m build --wheel

# Install the built wheel and dependencies
RUN pip install --no-cache-dir dist/*.whl

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim

# Metadata labels
LABEL maintainer="Allen R <allenr1@example.com>" \
      version="1.1.0" \
      description="NSIP MCP Server - Model Context Protocol server for NSIP sheep breeding data" \
      org.opencontainers.image.title="NSIP MCP Server" \
      org.opencontainers.image.description="FastMCP-based server providing LLM access to NSIP API" \
      org.opencontainers.image.version="1.1.0" \
      org.opencontainers.image.vendor="NSIP API Client Project" \
      org.opencontainers.image.source="https://github.com/epicpast/nsip-api-client" \
      org.opencontainers.image.licenses="MIT"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Default MCP transport configuration
    MCP_TRANSPORT=stdio \
    # Tiktoken cache directory (writable by non-root)
    TIKTOKEN_CACHE_DIR=/app/.cache/tiktoken \
    # Logging
    LOG_LEVEL=INFO

# Create non-root user for security
RUN groupadd -r nsip --gid=1000 && \
    useradd -r -g nsip --uid=1000 --home-dir=/app --shell=/bin/bash nsip

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Add venv to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Create cache directories with proper permissions
RUN mkdir -p /app/.cache/tiktoken && \
    chown -R nsip:nsip /app

# Switch to non-root user
USER nsip

# Expose ports for HTTP SSE and WebSocket transports
# These are only used if MCP_TRANSPORT is set to http-sse or websocket
EXPOSE 8000 9000

# Health check for HTTP SSE transport
# Only works when MCP_TRANSPORT=http-sse and MCP_PORT is set
# Fails gracefully for stdio transport
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD if [ "$MCP_TRANSPORT" = "http-sse" ] || [ "$MCP_TRANSPORT" = "websocket" ]; then \
            python -c "import urllib.request; urllib.request.urlopen('http://localhost:${MCP_PORT:-8000}/health').read()"; \
        else \
            exit 0; \
        fi

# Set entrypoint to the MCP server CLI
# This allows the container to accept stdio, HTTP SSE, or WebSocket connections
# based on environment variables
ENTRYPOINT ["nsip-mcp-server"]

# Default command (can be overridden)
# No additional arguments needed - configuration via environment variables
CMD []

# ============================================================================
# Usage Examples:
# ============================================================================
#
# Build the image:
#   docker build -t nsip-mcp-server:1.1.0 .
#   docker build -t nsip-mcp-server:latest .
#
# Run with stdio (default - for MCP clients):
#   docker run -i nsip-mcp-server:1.1.0
#
# Run with stdio and pipe JSON-RPC messages:
#   echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | docker run -i nsip-mcp-server:1.1.0
#
# Run with HTTP SSE:
#   docker run -p 8000:8000 -e MCP_TRANSPORT=http-sse -e MCP_PORT=8000 nsip-mcp-server:1.1.0
#
# Run with WebSocket:
#   docker run -p 9000:9000 -e MCP_TRANSPORT=websocket -e MCP_PORT=9000 nsip-mcp-server:1.1.0
#
# Run with custom host binding (HTTP SSE):
#   docker run -p 8000:8000 \
#     -e MCP_TRANSPORT=http-sse \
#     -e MCP_PORT=8000 \
#     -e MCP_HOST=0.0.0.0 \
#     nsip-mcp-server:1.1.0
#
# Run with debug logging:
#   docker run -p 8000:8000 \
#     -e MCP_TRANSPORT=http-sse \
#     -e MCP_PORT=8000 \
#     -e LOG_LEVEL=DEBUG \
#     nsip-mcp-server:1.1.0
#
# Run with custom tiktoken cache (persistent volume):
#   docker run -p 8000:8000 \
#     -e MCP_TRANSPORT=http-sse \
#     -e MCP_PORT=8000 \
#     -v tiktoken-cache:/app/.cache/tiktoken \
#     nsip-mcp-server:1.1.0
#
# Test health endpoint (HTTP SSE):
#   curl http://localhost:8000/health
#
# Interactive shell for debugging:
#   docker run -it --entrypoint /bin/bash nsip-mcp-server:1.1.0
#
# Check server version:
#   docker run nsip-mcp-server:1.1.0 --version
#
# ============================================================================
