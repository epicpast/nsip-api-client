# Docker Deployment Guide

Complete guide for deploying the NSIP MCP Server using Docker and Docker Compose.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Building the Image](#building-the-image)
3. [Running Containers](#running-containers)
4. [Docker Compose](#docker-compose)
5. [Configuration](#configuration)
6. [Production Deployment](#production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ (optional, for multi-service setup)

### Fastest Way to Run

```bash
# Build and run HTTP SSE mode on port 8000
docker-compose up

# Test the server
curl http://localhost:8000/health
```

That's it! The server is now running and accessible at `http://localhost:8000`.

---

## Building the Image

### Basic Build

```bash
# Build with default tag
docker build -t nsip-mcp-server:1.1.0 .

# Build with latest tag
docker build -t nsip-mcp-server:latest .

# Build with custom tag
docker build -t myorg/nsip-mcp-server:v1.1.0 .
```

### Build Arguments

The Dockerfile uses multi-stage builds for optimization. No build arguments are required.

### Build Optimization

```bash
# No cache build (clean build)
docker build --no-cache -t nsip-mcp-server:1.1.0 .

# Build with progress output
docker build --progress=plain -t nsip-mcp-server:1.1.0 .

# Build for specific platform
docker build --platform linux/amd64 -t nsip-mcp-server:1.1.0 .
```

### Verify Build

```bash
# Check image size
docker images nsip-mcp-server:1.1.0

# Expected output:
# REPOSITORY          TAG     IMAGE ID       CREATED         SIZE
# nsip-mcp-server     1.1.0   abc123def456   2 minutes ago   ~200MB

# Inspect image
docker inspect nsip-mcp-server:1.1.0
```

---

## Running Containers

### 1. stdio Mode (Default)

For MCP clients that communicate via standard input/output (like Claude Desktop when running in container).

```bash
# Interactive mode
docker run -i nsip-mcp-server:1.1.0

# Test with piped input
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | \
  docker run -i nsip-mcp-server:1.1.0

# Background mode (not typical for stdio)
docker run -d --name nsip-stdio nsip-mcp-server:1.1.0
```

**When to use:** Testing, integration with container-based MCP clients.

---

### 2. HTTP SSE Mode

For web applications and HTTP-based integrations.

```bash
# Basic HTTP SSE on port 8000
docker run -p 8000:8000 \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  nsip-mcp-server:1.1.0

# With custom port
docker run -p 9090:9090 \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=9090 \
  nsip-mcp-server:1.1.0

# Background mode (detached)
docker run -d -p 8000:8000 \
  --name nsip-http \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  nsip-mcp-server:1.1.0

# With restart policy
docker run -d -p 8000:8000 \
  --name nsip-http \
  --restart unless-stopped \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  nsip-mcp-server:1.1.0
```

**Test HTTP SSE:**
```bash
# Health check
curl http://localhost:8000/health

# List tools
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Call a tool
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"tools/call",
    "params":{
      "name":"nsip_list_breeds",
      "arguments":{}
    },
    "id":1
  }'
```

**When to use:** Web applications, browser clients, HTTP-only environments.

---

### 3. WebSocket Mode

For real-time bidirectional communication.

```bash
# Basic WebSocket on port 9000
docker run -p 9000:9000 \
  -e MCP_TRANSPORT=websocket \
  -e MCP_PORT=9000 \
  nsip-mcp-server:1.1.0

# Background mode
docker run -d -p 9000:9000 \
  --name nsip-websocket \
  -e MCP_TRANSPORT=websocket \
  -e MCP_PORT=9000 \
  nsip-mcp-server:1.1.0
```

**Test WebSocket:**
```bash
# Install wscat if needed
npm install -g wscat

# Connect
wscat -c ws://localhost:9000/ws

# Send message (after connected)
> {"jsonrpc":"2.0","method":"tools/list","id":1}

# You'll receive the response immediately
```

**When to use:** Real-time applications, persistent connections, low-latency requirements.

---

### 4. With Persistent Cache

Use a volume to persist the tiktoken cache across container restarts.

```bash
# Create named volume
docker volume create tiktoken-cache

# Run with volume
docker run -d -p 8000:8000 \
  --name nsip-http-persistent \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  -v tiktoken-cache:/app/.cache/tiktoken \
  nsip-mcp-server:1.1.0
```

**Benefits:**
- Faster startup (cache already initialized)
- Reduced network usage (don't re-download tokenizer)
- Consistent performance

---

### 5. With Debug Logging

Enable detailed logging for troubleshooting.

```bash
docker run -d -p 8000:8000 \
  --name nsip-debug \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  -e LOG_LEVEL=DEBUG \
  nsip-mcp-server:1.1.0

# View logs
docker logs -f nsip-debug
```

---

## Docker Compose

Docker Compose provides easy multi-service management with predefined configurations.

### Available Profiles

The `docker-compose.yml` includes several service profiles:

| Profile | Service | Port | Use Case |
|---------|---------|------|----------|
| `default` | HTTP SSE | 8000 | General use |
| `http` | HTTP SSE | 8000 | Web applications |
| `websocket` | WebSocket | 9000 | Real-time apps |
| `stdio` | stdio | - | Testing |
| `production` | HTTP SSE + cache | 8000 | Production deployment |
| `debug` | HTTP SSE + debug | 8000 | Development/debugging |

### Basic Usage

```bash
# Start default service (HTTP SSE)
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart
```

### Profile-Based Usage

```bash
# Start HTTP SSE mode
docker-compose --profile http up

# Start WebSocket mode
docker-compose --profile websocket up

# Start production mode (with persistent cache)
docker-compose --profile production up -d

# Start debug mode
docker-compose --profile debug up
```

### Service-Specific Commands

```bash
# Start specific service
docker-compose up nsip-mcp-http

# View service logs
docker-compose logs -f nsip-mcp-http

# Restart service
docker-compose restart nsip-mcp-http

# Stop service
docker-compose stop nsip-mcp-http

# Remove service
docker-compose rm nsip-mcp-http
```

### Development Workflow

```bash
# 1. Make code changes
# 2. Rebuild image
docker-compose build

# 3. Restart with new image
docker-compose up -d

# 4. View logs
docker-compose logs -f

# Alternative: rebuild and restart in one command
docker-compose up -d --build
```

### Production Deployment

```bash
# Start production services
docker-compose --profile production up -d

# Check health
curl http://localhost:8000/health

# View logs
docker-compose logs -f nsip-mcp-http-persistent

# Monitor performance
docker stats nsip-mcp-http-persistent
```

### Clean Up

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove containers, volumes, and images
docker-compose down -v --rmi all
```

---

## Configuration

### Environment Variables

Configure the server using environment variables:

| Variable | Default | Description | Example |
|----------|---------|-------------|---------|
| `MCP_TRANSPORT` | `stdio` | Transport type | `http-sse`, `websocket` |
| `MCP_PORT` | - | Port number | `8000`, `9000` |
| `MCP_HOST` | `0.0.0.0` | Bind address | `127.0.0.1`, `0.0.0.0` |
| `LOG_LEVEL` | `INFO` | Logging level | `DEBUG`, `INFO`, `WARNING` |
| `TIKTOKEN_CACHE_DIR` | `/app/.cache/tiktoken` | Cache directory | Any writable path |

### Configuration Methods

#### Method 1: Command Line

```bash
docker run -p 8000:8000 \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  -e LOG_LEVEL=DEBUG \
  nsip-mcp-server:1.1.0
```

#### Method 2: Environment File

Create `.env` file:
```bash
# .env
MCP_TRANSPORT=http-sse
MCP_PORT=8000
MCP_HOST=0.0.0.0
LOG_LEVEL=INFO
```

Use with Docker:
```bash
docker run -p 8000:8000 --env-file .env nsip-mcp-server:1.1.0
```

Use with Docker Compose:
```bash
docker-compose --env-file .env up
```

#### Method 3: docker-compose.yml Override

Create `docker-compose.override.yml`:
```yaml
version: '3.8'

services:
  nsip-mcp-http:
    environment:
      LOG_LEVEL: DEBUG
      MCP_PORT: 8080
    ports:
      - "8080:8080"
```

Docker Compose automatically loads this file:
```bash
docker-compose up
```

---

## Production Deployment

### Best Practices

#### 1. Use Specific Version Tags

```bash
# Good: Pinned version
docker run nsip-mcp-server:1.1.0

# Avoid: Latest tag (unpredictable)
docker run nsip-mcp-server:latest
```

#### 2. Set Resource Limits

```bash
docker run -p 8000:8000 \
  --memory="512m" \
  --cpus="1.0" \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  nsip-mcp-server:1.1.0
```

Docker Compose:
```yaml
services:
  nsip-mcp-http:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.5'
```

#### 3. Configure Restart Policy

```bash
docker run -p 8000:8000 \
  --restart unless-stopped \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  nsip-mcp-server:1.1.0
```

Docker Compose:
```yaml
services:
  nsip-mcp-http:
    restart: unless-stopped
```

#### 4. Use Health Checks

Already configured in Dockerfile, but you can customize:

```bash
docker run -p 8000:8000 \
  --health-cmd="python -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:8000/health\").read()'" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  nsip-mcp-server:1.1.0
```

#### 5. Enable Logging

```bash
docker run -p 8000:8000 \
  --log-driver=json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  nsip-mcp-server:1.1.0
```

#### 6. Use Persistent Volumes

```bash
docker run -p 8000:8000 \
  -v nsip-cache:/app/.cache/tiktoken \
  -e MCP_TRANSPORT=http-sse \
  -e MCP_PORT=8000 \
  nsip-mcp-server:1.1.0
```

### Complete Production Example

```yaml
version: '3.8'

services:
  nsip-mcp-server:
    image: nsip-mcp-server:1.1.0
    container_name: nsip-mcp-production
    environment:
      MCP_TRANSPORT: http-sse
      MCP_PORT: 8000
      MCP_HOST: 0.0.0.0
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    volumes:
      - tiktoken-cache:/app/.cache/tiktoken
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.5'
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  tiktoken-cache:
    driver: local
```

Deploy:
```bash
docker-compose -f docker-compose.production.yml up -d
```

### Monitoring

```bash
# Container stats
docker stats nsip-mcp-production

# Health status
docker inspect --format='{{json .State.Health}}' nsip-mcp-production | jq

# View logs
docker logs -f --tail=100 nsip-mcp-production

# Check server health
curl http://localhost:8000/health | jq
```

---

## Troubleshooting

### Issue 1: Container Exits Immediately

**Symptoms:**
```bash
docker ps -a
# Shows container with "Exited (1)" status
```

**Debug:**
```bash
# View logs
docker logs nsip-mcp-server

# Run interactively
docker run -it --entrypoint /bin/bash nsip-mcp-server:1.1.0
```

**Common Causes:**
- Missing MCP_PORT for http-sse/websocket
- Invalid environment variable values
- Port already in use

---

### Issue 2: Port Already in Use

**Symptoms:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
docker run -p 8080:8000 -e MCP_TRANSPORT=http-sse -e MCP_PORT=8000 nsip-mcp-server:1.1.0
```

---

### Issue 3: Health Check Failing

**Symptoms:**
```bash
docker ps
# Shows "unhealthy" status
```

**Debug:**
```bash
# Check health check logs
docker inspect --format='{{json .State.Health}}' nsip-mcp-server | jq

# Manual health check
docker exec nsip-mcp-server python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read())"
```

**Common Causes:**
- Server not fully started (wait for start_period)
- Wrong MCP_PORT configuration
- Application error (check logs)

---

### Issue 4: Cannot Connect to Server

**Symptoms:**
```bash
curl http://localhost:8000/health
# Connection refused
```

**Debug:**
```bash
# Check if container is running
docker ps | grep nsip

# Check port mapping
docker port nsip-mcp-http

# Check logs
docker logs nsip-mcp-http

# Test from inside container
docker exec nsip-mcp-http curl http://localhost:8000/health
```

**Common Causes:**
- Container not running
- Wrong port mapping (-p 8000:9000 when MCP_PORT=8000)
- Firewall blocking access

---

### Issue 5: Performance Issues

**Symptoms:**
- Slow response times
- High memory usage
- Container restarts

**Debug:**
```bash
# Monitor resources
docker stats nsip-mcp-http

# Check container logs for errors
docker logs nsip-mcp-http | grep -i error

# Check server health metrics
curl http://localhost:8000/health | jq
```

**Solutions:**
- Increase memory limit: `--memory="1g"`
- Use persistent volume for cache
- Check NSIP API status
- Review summarization performance in health metrics

---

### Issue 6: Cache Not Persisting

**Symptoms:**
- Slow startup after restart
- Tiktoken re-downloading

**Solution:**
```bash
# Create named volume
docker volume create tiktoken-cache

# Use volume
docker run -v tiktoken-cache:/app/.cache/tiktoken ...

# Verify volume
docker volume inspect tiktoken-cache
```

---

### Getting Help

**Collect debugging information:**

```bash
# Container info
docker inspect nsip-mcp-http > container-info.json

# Logs
docker logs nsip-mcp-http > container-logs.txt

# Health metrics
curl http://localhost:8000/health > health-metrics.json

# System info
docker version
docker info
uname -a
```

**Report issues at:** https://github.com/epicpast/nsip-api-client/issues

---

## Additional Resources

- [MCP Server Documentation](./mcp-server.md)
- [Main README](../README.md)
- [Docker Hub Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

*Last Updated: October 11, 2025*
