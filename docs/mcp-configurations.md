# MCP Configuration Guide

Complete configuration reference for deploying the NSIP MCP Server across different environments and clients. This guide provides copy-pasteable configurations for Claude Desktop, Docker, and various transport methods.

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Claude Desktop Configurations](#claude-desktop-configurations)
3. [UVX Configurations](#uvx-configurations)
4. [Docker Configurations](#docker-configurations)
5. [Streamable HTTP Transport](#streamable-http-transport)
6. [WebSocket Transport](#websocket-transport)
7. [Development/Local Configurations](#developmentlocal-configurations)
8. [Environment Variables Reference](#environment-variables-reference)
9. [Configuration Troubleshooting](#configuration-troubleshooting)

---

## Quick Reference

| Deployment Method | Best For | Prerequisites |
|-------------------|----------|---------------|
| uvx | Quick setup, no installation | uv installed |
| pip install | Permanent installation | Python 3.10+ |
| Docker (ghcr.io) | Isolated environments, no build | Docker 20.10+ |
| From source | Development | Git, Python 3.10+ |

| Transport | Port Required | Use Case |
|-----------|---------------|----------|
| stdio | No | Claude Desktop, CLI tools |
| streamable-http | Yes | Web apps, REST clients |
| websocket | Yes | Real-time apps |

---

## Claude Desktop Configurations

Claude Desktop configuration file locations:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Option 1: Using uvx (Recommended)

The simplest configuration - no installation required. uvx automatically downloads and runs the package.

```json
{
  "mcpServers": {
    "nsip": {
      "command": "uvx",
      "args": ["nsip-mcp-server"]
    }
  }
}
```

**With specific version pinning:**

```json
{
  "mcpServers": {
    "nsip": {
      "command": "uvx",
      "args": [
        "--from",
        "nsip-mcp-server==1.3.4",
        "nsip-mcp-server"
      ]
    }
  }
}
```

**Installing from GitHub (latest or specific tag):**

```json
{
  "mcpServers": {
    "nsip": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/epicpast/nsip-api-client@v1.3.4",
        "nsip-mcp-server"
      ]
    }
  }
}
```

**Prerequisites:**
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Ensure `~/.cargo/bin` (or uv install location) is in your PATH

---

### Option 2: Using pip-installed Package

For users who prefer a permanent installation.

**Step 1: Install the package**

```bash
# From PyPI (when published)
pip install nsip-mcp-server

# From GitHub
pip install git+https://github.com/epicpast/nsip-api-client.git
```

**Step 2: Configure Claude Desktop**

```json
{
  "mcpServers": {
    "nsip": {
      "command": "nsip-mcp-server"
    }
  }
}
```

**If the command is not in PATH, use full path:**

```json
{
  "mcpServers": {
    "nsip": {
      "command": "/Users/YOUR_USERNAME/.local/bin/nsip-mcp-server"
    }
  }
}
```

**Find the installed path:**

```bash
which nsip-mcp-server
# or
python -c "import shutil; print(shutil.which('nsip-mcp-server'))"
```

---

### Option 3: Using Docker

For isolated, reproducible deployments using pre-built images from GitHub Container Registry.

**Step 1: Pull the image from GitHub Container Registry**

```bash
# Pull latest release
docker pull ghcr.io/epicpast/nsip-mcp-server:latest

# Or pull a specific version
docker pull ghcr.io/epicpast/nsip-mcp-server:1.3.4
```

**Step 2: Configure Claude Desktop**

```json
{
  "mcpServers": {
    "nsip": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/epicpast/nsip-mcp-server:latest"
      ]
    }
  }
}
```

**With specific version (recommended for production):**

```json
{
  "mcpServers": {
    "nsip": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/epicpast/nsip-mcp-server:1.3.4"
      ]
    }
  }
}
```

**Note:** The `-i` flag is required for stdio transport to work with Docker.

**Available image tags:**
- `latest` - Most recent stable release
- `1.3.4`, `1.3.3`, etc. - Specific version releases
- `main` - Latest from main branch (development)

---

### Option 4: Using Python Module Directly

For development or when the package entry point is not available.

```json
{
  "mcpServers": {
    "nsip": {
      "command": "python",
      "args": ["-m", "nsip_mcp.cli"]
    }
  }
}
```

**With explicit Python path:**

```json
{
  "mcpServers": {
    "nsip": {
      "command": "/usr/local/bin/python3",
      "args": ["-m", "nsip_mcp.cli"]
    }
  }
}
```

---

### Multiple Server Configuration

Configure NSIP alongside other MCP servers:

```json
{
  "mcpServers": {
    "nsip": {
      "command": "uvx",
      "args": ["nsip-mcp-server"]
    },
    "filesystem": {
      "command": "uvx",
      "args": ["mcp-server-filesystem", "--root", "/Users/YOUR_USERNAME/Documents"]
    },
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

---

## UVX Configurations

uvx provides zero-installation execution of Python packages.

### Basic Usage

```bash
# Run the server directly
uvx nsip-mcp-server

# Run specific version
uvx nsip-mcp-server==1.3.4

# Run from GitHub
uvx --from git+https://github.com/epicpast/nsip-api-client nsip-mcp-server
```

### With Environment Variables

```bash
# HTTP transport
MCP_TRANSPORT=streamable-http MCP_PORT=8000 uvx nsip-mcp-server

# WebSocket transport
MCP_TRANSPORT=websocket MCP_PORT=9000 uvx nsip-mcp-server

# Debug logging
LOG_LEVEL=DEBUG uvx nsip-mcp-server
```

### UVX with Virtual Environment Isolation

```bash
# Create isolated environment with specific Python version
uvx --python 3.11 nsip-mcp-server

# Force fresh installation (ignore cache)
uvx --reinstall nsip-mcp-server
```

### Claude Desktop with uvx and Environment Variables

```json
{
  "mcpServers": {
    "nsip": {
      "command": "uvx",
      "args": ["nsip-mcp-server"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

---

## Docker Configurations

Pre-built Docker images are available from GitHub Container Registry. No build required!

### Quick Start with Pre-built Images

```bash
# Pull the latest release
docker pull ghcr.io/epicpast/nsip-mcp-server:latest

# Or pull a specific version
docker pull ghcr.io/epicpast/nsip-mcp-server:1.3.4

# Run stdio mode (for Claude Desktop)
docker run -i --rm ghcr.io/epicpast/nsip-mcp-server:latest

# Run HTTP mode
docker run -d -p 8000:8000 \
  -e MCP_TRANSPORT=streamable-http \
  -e MCP_PORT=8000 \
  --name nsip-http \
  ghcr.io/epicpast/nsip-mcp-server:latest
```

### docker-compose.yml

Complete docker-compose configuration using pre-built images:

```yaml
version: '3.8'

services:
  # stdio mode (for MCP clients like Claude Desktop)
  nsip-mcp-stdio:
    image: ghcr.io/epicpast/nsip-mcp-server:1.3.4
    container_name: nsip-mcp-stdio
    environment:
      MCP_TRANSPORT: stdio
      LOG_LEVEL: INFO
    stdin_open: true
    tty: false
    restart: unless-stopped
    profiles:
      - stdio

  # Streamable HTTP mode (for web applications)
  nsip-mcp-http:
    image: ghcr.io/epicpast/nsip-mcp-server:1.3.4
    container_name: nsip-mcp-http
    environment:
      MCP_TRANSPORT: streamable-http
      MCP_PORT: 8000
      MCP_HOST: 0.0.0.0
      MCP_PATH: /mcp
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    profiles:
      - http
      - default

  # WebSocket mode (for real-time applications)
  nsip-mcp-websocket:
    image: ghcr.io/epicpast/nsip-mcp-server:1.3.4
    container_name: nsip-mcp-websocket
    environment:
      MCP_TRANSPORT: websocket
      MCP_PORT: 9000
      MCP_HOST: 0.0.0.0
      LOG_LEVEL: INFO
    ports:
      - "9000:9000"
    restart: unless-stopped
    profiles:
      - websocket

  # Production mode with persistent cache
  nsip-mcp-production:
    image: ghcr.io/epicpast/nsip-mcp-server:1.3.4
    container_name: nsip-mcp-production
    environment:
      MCP_TRANSPORT: streamable-http
      MCP_PORT: 8000
      MCP_HOST: 0.0.0.0
      LOG_LEVEL: INFO
      TIKTOKEN_CACHE_DIR: /app/.cache/tiktoken
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
    profiles:
      - production

volumes:
  tiktoken-cache:
    driver: local
    name: nsip-mcp-tiktoken-cache
```

### Docker Commands Reference

```bash
# Pull the latest image
docker pull ghcr.io/epicpast/nsip-mcp-server:latest

# Run stdio mode (for Claude Desktop)
docker run -i --rm ghcr.io/epicpast/nsip-mcp-server:latest

# Run Streamable HTTP mode
docker run -d -p 8000:8000 \
  -e MCP_TRANSPORT=streamable-http \
  -e MCP_PORT=8000 \
  --name nsip-http \
  ghcr.io/epicpast/nsip-mcp-server:latest

# Run WebSocket mode
docker run -d -p 9000:9000 \
  -e MCP_TRANSPORT=websocket \
  -e MCP_PORT=9000 \
  --name nsip-ws \
  ghcr.io/epicpast/nsip-mcp-server:latest

# Run with persistent cache
docker run -d -p 8000:8000 \
  -e MCP_TRANSPORT=streamable-http \
  -e MCP_PORT=8000 \
  -v nsip-cache:/app/.cache/tiktoken \
  --name nsip-http \
  ghcr.io/epicpast/nsip-mcp-server:latest

# Docker Compose commands
docker-compose up                           # Start default (HTTP) service
docker-compose --profile websocket up       # Start WebSocket service
docker-compose --profile production up -d   # Start production service
docker-compose down                         # Stop all services
docker-compose down -v                      # Stop and remove volumes
```

### Claude Desktop with Docker

```json
{
  "mcpServers": {
    "nsip": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "ghcr.io/epicpast/nsip-mcp-server:latest"
      ]
    }
  }
}
```

### Building from Source (Optional)

If you need to build a custom image (for development or modifications):

```bash
git clone https://github.com/epicpast/nsip-api-client.git
cd nsip-api-client
docker build -t nsip-mcp-server:custom .
```

See the [Dockerfile](../Dockerfile) in the repository for the full build configuration.

---

## Streamable HTTP Transport

Use Streamable HTTP for web applications, browser-based clients, and HTTP-only environments.

### Configuration

```bash
# Start server
MCP_TRANSPORT=streamable-http MCP_PORT=8000 nsip-mcp-server

# With all options
MCP_TRANSPORT=streamable-http \
MCP_PORT=8000 \
MCP_HOST=0.0.0.0 \
MCP_PATH=/mcp \
LOG_LEVEL=INFO \
nsip-mcp-server
```

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp` | POST | JSON-RPC 2.0 message endpoint |
| `/mcp/sse` | GET | Server-Sent Events stream |
| `/health` | GET | Health check endpoint |

### Client Examples

**curl:**

```bash
# Health check
curl http://localhost:8000/health

# List tools
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Call a tool
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "method":"tools/call",
    "params":{
      "name":"nsip_list_breeds",
      "arguments":{}
    },
    "id":2
  }'
```

**Python (requests):**

```python
import requests

base_url = "http://localhost:8000"

# Health check
response = requests.get(f"{base_url}/health")
print(response.json())

# Call tool
response = requests.post(
    f"{base_url}/mcp",
    json={
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "nsip_get_animal",
            "arguments": {"search_string": "6332-12345"}
        },
        "id": 1
    }
)
print(response.json())
```

**JavaScript (fetch):**

```javascript
const baseUrl = 'http://localhost:8000';

// Call tool
const response = await fetch(`${baseUrl}/mcp`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    jsonrpc: '2.0',
    method: 'tools/call',
    params: {
      name: 'nsip_list_breeds',
      arguments: {}
    },
    id: 1
  })
});
const data = await response.json();
console.log(data);
```

### When to Use Streamable HTTP

- Web applications with REST-style communication
- Browser-based MCP clients
- Environments where WebSocket is not available
- Load balancer and reverse proxy setups
- Serverless deployments (with persistent container)

### Nginx Reverse Proxy Configuration

```nginx
upstream nsip_mcp {
    server localhost:8000;
}

server {
    listen 443 ssl;
    server_name mcp.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /mcp {
        proxy_pass http://nsip_mcp;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE support
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 86400s;
    }

    location /health {
        proxy_pass http://nsip_mcp;
    }
}
```

---

## WebSocket Transport

Use WebSocket for real-time bidirectional communication with low latency.

### Configuration

```bash
# Start server
MCP_TRANSPORT=websocket MCP_PORT=9000 nsip-mcp-server

# With all options
MCP_TRANSPORT=websocket \
MCP_PORT=9000 \
MCP_HOST=0.0.0.0 \
LOG_LEVEL=INFO \
nsip-mcp-server
```

### Connection URL

```
ws://localhost:9000/ws
```

### Client Examples

**wscat (command line):**

```bash
# Install
npm install -g wscat

# Connect
wscat -c ws://localhost:9000/ws

# Send message (after connected)
> {"jsonrpc":"2.0","method":"tools/list","id":1}
```

**Python (websockets):**

```python
import asyncio
import websockets
import json

async def call_tool():
    uri = "ws://localhost:9000/ws"
    async with websockets.connect(uri) as websocket:
        # Send request
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "nsip_get_animal",
                "arguments": {"search_string": "6332-12345"}
            },
            "id": 1
        }
        await websocket.send(json.dumps(request))

        # Receive response
        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(call_tool())
```

**JavaScript (browser):**

```javascript
const ws = new WebSocket('ws://localhost:9000/ws');

ws.onopen = () => {
  console.log('Connected');

  // Send request
  ws.send(JSON.stringify({
    jsonrpc: '2.0',
    method: 'tools/call',
    params: {
      name: 'nsip_list_breeds',
      arguments: {}
    },
    id: 1
  }));
};

ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log('Response:', response);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected');
};
```

### When to Use WebSocket

- Real-time applications requiring push notifications
- Low-latency requirements
- Long-running connections
- Bidirectional communication needs
- Native mobile applications

### WebSocket Keep-Alive

Implement ping/pong to maintain connections:

```javascript
const ws = new WebSocket('ws://localhost:9000/ws');
let pingInterval;

ws.onopen = () => {
  // Send ping every 30 seconds
  pingInterval = setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        jsonrpc: '2.0',
        method: 'ping',
        id: Date.now()
      }));
    }
  }, 30000);
};

ws.onclose = () => {
  clearInterval(pingInterval);
  // Implement reconnection logic
  setTimeout(() => connect(), 1000);
};
```

---

## Development/Local Configurations

### Running from Source

**Step 1: Clone and setup**

```bash
git clone https://github.com/epicpast/nsip-api-client.git
cd nsip-api-client

# Using uv (recommended)
uv sync --all-extras

# Or traditional venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -e ".[dev]"
```

**Step 2: Run the server**

```bash
# Using uv
uv run nsip-mcp-server

# Using activated venv
nsip-mcp-server

# Or as Python module
python -m nsip_mcp.cli
```

### Claude Desktop for Development

**Using uv run:**

```json
{
  "mcpServers": {
    "nsip-dev": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/nsip-api-client", "nsip-mcp-server"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**Using Python from venv:**

```json
{
  "mcpServers": {
    "nsip-dev": {
      "command": "/path/to/nsip-api-client/venv/bin/python",
      "args": ["-m", "nsip_mcp.cli"],
      "env": {
        "LOG_LEVEL": "DEBUG",
        "PYTHONPATH": "/path/to/nsip-api-client/src"
      }
    }
  }
}
```

### Testing Configurations

**Test stdio locally:**

```bash
# Send a test message
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | nsip-mcp-server
```

**Test HTTP locally:**

```bash
# Terminal 1: Start server
MCP_TRANSPORT=streamable-http MCP_PORT=8000 nsip-mcp-server

# Terminal 2: Test
curl http://localhost:8000/health
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

### VS Code Launch Configuration

Add to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "NSIP MCP Server (stdio)",
      "type": "debugpy",
      "request": "launch",
      "module": "nsip_mcp.cli",
      "console": "integratedTerminal",
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    },
    {
      "name": "NSIP MCP Server (HTTP)",
      "type": "debugpy",
      "request": "launch",
      "module": "nsip_mcp.cli",
      "console": "integratedTerminal",
      "env": {
        "MCP_TRANSPORT": "streamable-http",
        "MCP_PORT": "8000",
        "LOG_LEVEL": "DEBUG"
      }
    }
  ]
}
```

---

## Environment Variables Reference

### Complete Reference Table

| Variable | Description | Default | Valid Values | Required |
|----------|-------------|---------|--------------|----------|
| `MCP_TRANSPORT` | Transport mechanism | `stdio` | `stdio`, `streamable-http`, `websocket` | No |
| `MCP_PORT` | Port for HTTP/WebSocket | None | 1024-65535 | Yes (for non-stdio) |
| `MCP_HOST` | Host address to bind | `0.0.0.0` | Valid IP/hostname | No |
| `MCP_PATH` | HTTP endpoint path | `/mcp` | Valid URL path | No |
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | No |
| `TIKTOKEN_CACHE_DIR` | Token cache directory | OS default | Valid writable path | No |

### Transport-Specific Requirements

| Transport | Required Variables | Optional Variables |
|-----------|-------------------|-------------------|
| stdio | None | `LOG_LEVEL` |
| streamable-http | `MCP_PORT` | `MCP_HOST`, `MCP_PATH`, `LOG_LEVEL` |
| websocket | `MCP_PORT` | `MCP_HOST`, `LOG_LEVEL` |

### Configuration Examples by Use Case

**Development (verbose logging):**

```bash
export LOG_LEVEL=DEBUG
nsip-mcp-server
```

**Production HTTP (all interfaces, port 8000):**

```bash
export MCP_TRANSPORT=streamable-http
export MCP_PORT=8000
export MCP_HOST=0.0.0.0
export LOG_LEVEL=INFO
nsip-mcp-server
```

**Secure deployment (localhost only):**

```bash
export MCP_TRANSPORT=streamable-http
export MCP_PORT=8000
export MCP_HOST=127.0.0.1
nsip-mcp-server
```

**Custom endpoint path:**

```bash
export MCP_TRANSPORT=streamable-http
export MCP_PORT=8000
export MCP_PATH=/api/v1/mcp
nsip-mcp-server
```

### Environment File (.env)

Create a `.env` file for easier configuration:

```bash
# .env
MCP_TRANSPORT=streamable-http
MCP_PORT=8000
MCP_HOST=0.0.0.0
MCP_PATH=/mcp
LOG_LEVEL=INFO
TIKTOKEN_CACHE_DIR=/var/cache/nsip-mcp/tiktoken
```

**Use with shell:**

```bash
# Load and run
export $(cat .env | xargs) && nsip-mcp-server

# Or use direnv
echo 'dotenv' > .envrc
direnv allow
nsip-mcp-server
```

**Use with Docker:**

```bash
docker run --env-file .env -p 8000:8000 ghcr.io/epicpast/nsip-mcp-server:latest
```

**Use with Docker Compose:**

```yaml
services:
  nsip-mcp:
    image: ghcr.io/epicpast/nsip-mcp-server:latest
    env_file:
      - .env
    ports:
      - "8000:8000"
```

---

## Configuration Troubleshooting

### Common Issues and Solutions

#### Issue: "MCP_PORT environment variable required"

**Cause:** Using HTTP or WebSocket transport without setting the port.

**Solution:**

```bash
# Set the required port
export MCP_PORT=8000
MCP_TRANSPORT=streamable-http nsip-mcp-server
```

#### Issue: "Invalid MCP_TRANSPORT"

**Cause:** Typo in transport name or using unsupported value.

**Solution:**

```bash
# Valid transport values
MCP_TRANSPORT=stdio           # Default
MCP_TRANSPORT=streamable-http # HTTP with SSE
MCP_TRANSPORT=websocket       # WebSocket

# Note: "http-sse" is supported for backward compatibility
# but "streamable-http" is preferred
```

#### Issue: "Port must be between 1024 and 65535"

**Cause:** Using a privileged port (< 1024) or invalid port number.

**Solution:**

```bash
# Use a valid unprivileged port
MCP_PORT=8000  # Good
MCP_PORT=80    # Bad (privileged)
MCP_PORT=70000 # Bad (out of range)
```

#### Issue: Claude Desktop shows "Server not responding"

**Possible causes and solutions:**

1. **Command not found:**
   ```json
   {
     "mcpServers": {
       "nsip": {
         "command": "/full/path/to/nsip-mcp-server"
       }
     }
   }
   ```

2. **Python not in PATH:**
   ```json
   {
     "mcpServers": {
       "nsip": {
         "command": "/usr/local/bin/python3",
         "args": ["-m", "nsip_mcp.cli"]
       }
     }
   }
   ```

3. **uvx not in PATH:**
   ```json
   {
     "mcpServers": {
       "nsip": {
         "command": "/Users/YOUR_USERNAME/.cargo/bin/uvx",
         "args": ["nsip-mcp-server"]
       }
     }
   }
   ```

#### Issue: Docker container exits immediately

**Cause:** Missing `-i` flag for stdio mode.

**Solution:**

```bash
# For stdio mode, always use -i
docker run -i --rm ghcr.io/epicpast/nsip-mcp-server:latest

# For HTTP/WebSocket, ensure port mapping
docker run -d -p 8000:8000 \
  -e MCP_TRANSPORT=streamable-http \
  -e MCP_PORT=8000 \
  ghcr.io/epicpast/nsip-mcp-server:latest
```

#### Issue: "Address already in use"

**Cause:** Port is already bound by another process.

**Solution:**

```bash
# Find process using the port
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
MCP_PORT=8080 MCP_TRANSPORT=streamable-http nsip-mcp-server
```

#### Issue: Cannot connect from remote host

**Cause:** Server bound to localhost only.

**Solution:**

```bash
# Bind to all interfaces
MCP_HOST=0.0.0.0 MCP_PORT=8000 MCP_TRANSPORT=streamable-http nsip-mcp-server

# Check firewall rules
sudo ufw allow 8000/tcp
```

### Verification Commands

**Verify installation:**

```bash
# Check if command exists
which nsip-mcp-server

# Check version
nsip-mcp-server --version || python -c "import nsip_mcp; print(nsip_mcp.__version__)"

# Test basic functionality
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"id":1}' | nsip-mcp-server
```

**Verify Docker image:**

```bash
# List images
docker images | grep nsip

# Test stdio mode
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | docker run -i --rm ghcr.io/epicpast/nsip-mcp-server:latest

# Test HTTP mode
docker run -d -p 8000:8000 -e MCP_TRANSPORT=streamable-http -e MCP_PORT=8000 --name nsip-test ghcr.io/epicpast/nsip-mcp-server:latest
curl http://localhost:8000/health
docker rm -f nsip-test
```

**Verify Claude Desktop configuration:**

1. Restart Claude Desktop after config changes
2. Look for NSIP in the MCP servers list
3. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`
   - Linux: `~/.local/share/Claude/logs/`

### Debug Mode

Enable comprehensive logging for troubleshooting:

```bash
# Shell
LOG_LEVEL=DEBUG nsip-mcp-server 2>&1 | tee nsip-debug.log

# Claude Desktop
{
  "mcpServers": {
    "nsip": {
      "command": "nsip-mcp-server",
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

---

## Additional Resources

- [MCP Server Documentation](./mcp-server.md) - Detailed server features and API
- [Docker Deployment Guide](./docker.md) - In-depth Docker configuration
- [MCP Resources Reference](./mcp-resources.md) - Available MCP resources
- [MCP Prompts Reference](./mcp-prompts.md) - Available MCP prompts
- [Shepherd Agent Guide](./shepherd-agent.md) - AI breeding advisor

---

*Last Updated: December 2025*
