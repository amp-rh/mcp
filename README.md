# MCP Router

[![Install](https://img.shields.io/badge/pip-install%20from%20github-blue)](https://github.com/amp-rh/mcp)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-50%20passing-brightgreen.svg)](#testing)
[![FastMCP](https://img.shields.io/badge/FastMCP-compatible-purple)](https://gofastmcp.com)

A production-ready MCP router that aggregates and routes requests to multiple MCP backend servers. Built with FastMCP and featuring advanced routing strategies, health checking, and circuit breaker patterns.

**Quick Install:** `pip install git+https://github.com/amp-rh/mcp.git`

## Features

- **Multi-Backend Aggregation**: Route requests across multiple MCP servers
- **Three Routing Strategies**:
  - Path-based routing (glob patterns)
  - Capability-based routing (query backend capabilities)
  - Priority/fallback chains
- **Namespace Prefixing**: Prevent naming conflicts with `backend.tool_name` syntax
- **Health Checking**: Active probes + passive monitoring with circuit breaker pattern
- **Retry Logic**: Exponential backoff for transient failures
- **Router Management Tools**: Monitor backend health and routing decisions
- **YAML Configuration**: Simple backend definitions with environment variable overrides
- **FastMCP**: High-level Python framework for MCP servers
- **HTTP/SSE Transport**: Ready for web deployment
- **Container Support**: UBI9 rootless container for enterprise deployments
- **Modern Python Tooling**: uv, pytest, ruff

## Quick Start

### For Claude Desktop Users

1. **Add to Claude Desktop configuration:**

```json
{
  "mcpServers": {
    "mcp-router": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "git+https://github.com/amp-rh/mcp.git",
        "mcp-router"
      ]
    }
  }
}
```

2. **Restart Claude Desktop**

3. **Done!** The router tools are now available in Claude Desktop

### For Local Development

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/amp-rh/mcp.git
cd mcp
uv sync --all-extras

# Copy example configuration
cp config/backends.yaml.example config/backends.yaml

# Run tests (50+ tests covering all routing functionality)
make test

# Run the router server locally
make run
```

The router will be available at `http://localhost:8000` and expose all backend tools with namespace prefixes.

## Installation

### Method 1: Install from GitHub (Recommended)

```bash
pip install git+https://github.com/amp-rh/mcp.git
```

After installation, you can run:
```bash
# Template mode (simple MCP server)
mcp-server

# Router mode (multi-backend aggregation)
mcp-router
```

### Method 2: Install with uv

```bash
uv pip install git+https://github.com/amp-rh/mcp.git
```

### Method 3: Development Installation

```bash
git clone https://github.com/amp-rh/mcp.git
cd mcp
uv sync --all-extras
```

## Claude Desktop Integration

To use this MCP router with Claude Desktop, add to your MCP settings:

### Option 1: Using uv (Recommended)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "mcp-router": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "git+https://github.com/amp-rh/mcp.git",
        "mcp-router"
      ],
      "env": {
        "MCP_BACKENDS_CONFIG": "/path/to/your/config/backends.yaml"
      }
    }
  }
}
```

### Option 2: Using Installed Package

If you've installed via pip:

```json
{
  "mcpServers": {
    "mcp-router": {
      "command": "mcp-router",
      "env": {
        "MCP_BACKENDS_CONFIG": "/path/to/your/config/backends.yaml"
      }
    }
  }
}
```

### Option 3: Using FastMCP CLI

```bash
# Install the router
pip install git+https://github.com/amp-rh/mcp.git

# Configure for Claude Desktop
fastmcp install claude-desktop mcp_server.server:mcp --name mcp-router
```

### Option 4: Template Mode (No Routing)

For simple template mode without routing:

```json
{
  "mcpServers": {
    "mcp-template": {
      "command": "mcp-server"
    }
  }
}
```

**Note:** After updating configuration, restart Claude Desktop for changes to take effect.

## Configuration for Claude Desktop

### Step 1: Create Backend Configuration

Create or edit `config/backends.yaml`:

```yaml
backends:
  - name: my-backend
    url: http://localhost:8001
    namespace: backend
    priority: 10
    routes:
      - pattern: "*"
        strategy: capability
    health_check:
      enabled: true
      interval_seconds: 30
    circuit_breaker:
      failure_threshold: 5
      timeout_seconds: 60
```

### Step 2: Set Environment Variable

Point Claude Desktop to your config file:

```json
{
  "mcpServers": {
    "mcp-router": {
      "command": "mcp-router",
      "env": {
        "MCP_BACKENDS_CONFIG": "/absolute/path/to/config/backends.yaml"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

Restart Claude Desktop to load the MCP server.

### Troubleshooting

**Server not appearing:**
- Check Claude Desktop logs at `~/Library/Logs/Claude/mcp*.log` (macOS)
- Verify backend config file path is absolute
- Ensure backend MCP servers are running

**Connection errors:**
- Verify backend URLs are correct
- Check backend servers are accessible
- Review health check settings in config

**Tool conflicts:**
- Enable namespace prefixing to avoid naming conflicts
- Use unique namespaces for each backend

## Routing Configuration

### Step 1: Create Backend Configuration

Create `config/backends.yaml` from the example:

```yaml
backends:
  - name: database
    url: http://localhost:8001
    namespace: db
    priority: 10
    routes:
      - pattern: "*_user"
        strategy: path
    health_check:
      enabled: true
      interval_seconds: 30
    circuit_breaker:
      failure_threshold: 5
      timeout_seconds: 60
```

### Step 2: Run Backend MCP Servers

```bash
# Terminal 1: Backend 1
uv run fastmcp run path/to/backend1:mcp --transport sse --port 8001

# Terminal 2: Backend 2
uv run fastmcp run path/to/backend2:mcp --transport sse --port 8002
```

### Step 3: Start the Router

```bash
make run
# Router starts on http://localhost:8000
```

## Routing Strategies

The router supports three routing strategies per backend:

### Path-Based Routing
```yaml
routes:
  - pattern: "fetch_*"
    strategy: path
  - pattern: "*_user"
    strategy: path
```
Routes tools based on glob patterns matching the tool name.

### Capability-Based Routing
```yaml
routes:
  - pattern: "*"
    strategy: capability
```
Queries backend capabilities and routes to backends that have the tool.

### Fallback Chains
```yaml
routes:
  - pattern: "analyze_*"
    strategy: fallback
    fallback_to: analytics-secondary
```
Tries primary backend first, falls back to secondary if circuit is open.

## Namespace Prefixing

When namespace prefixing is enabled (default), tools from different backends are exposed with prefixes:

```
Tool on 'db' backend:       fetch_user  →  db.fetch_user
Tool on 'api' backend:      fetch_user  →  api.fetch_user
Tool on 'analytics' backend: analyze    →  analytics.analyze
```

This prevents naming conflicts when aggregating tools from multiple backends.

## Health Checking & Circuit Breaker

The router monitors backend health with:

- **Active Probing**: Periodic health checks to `/health` endpoint
- **Passive Monitoring**: Tracks errors from actual requests
- **Circuit Breaker States**:
  - `CLOSED`: Normal operation (requests flow through)
  - `OPEN`: Backend unhealthy (requests rejected immediately)
  - `HALF_OPEN`: Testing recovery (allows limited requests)

Configure per backend:

```yaml
circuit_breaker:
  failure_threshold: 5        # Failures before opening circuit
  timeout_seconds: 60         # Wait time before HALF_OPEN test
  half_open_attempts: 3       # Attempts in HALF_OPEN state
```

## Router Management Tools

The router exposes three management tools:

### list_backends()
Lists all configured backends with health status:

```json
{
  "name": "database",
  "url": "http://localhost:8001",
  "namespace": "db",
  "priority": 10,
  "healthy": true,
  "circuit_state": "CLOSED",
  "error_count": 0
}
```

### get_backend_health(backend_name)
Gets detailed health information for a specific backend:

```json
{
  "name": "database",
  "healthy": true,
  "circuit_state": "CLOSED",
  "error_count": 0,
  "last_error": null
}
```

## Environment Variables

For dynamic configuration override:

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_NAME` | `mcp-router` | Router server name |
| `MCP_HOST` | `0.0.0.0` | Host to bind to |
| `MCP_PORT` | `8000` | Port to listen on |
| `MCP_BACKENDS_CONFIG` | `config/backends.yaml` | Backend config file path |
| `MCP_DEFAULT_STRATEGY` | `capability` | Default routing strategy |
| `MCP_ENABLE_NAMESPACES` | `true` | Enable namespace prefixing |
| `MCP_CACHE_TTL` | `300` | Capability cache TTL (seconds) |
| `MCP_REQUEST_TIMEOUT` | `30` | Backend request timeout (seconds) |
| `MCP_HEALTH_CHECK_INTERVAL` | `30` | Health check interval (seconds) |
| `MCP_HEALTH_CHECK_TIMEOUT` | `5` | Health check timeout (seconds) |
| `MCP_MAX_RETRIES` | `3` | Max retry attempts |
| `MCP_RETRY_BACKOFF` | `2.0` | Exponential backoff multiplier |
| `MCP_MAX_BACKOFF` | `10` | Max backoff time (seconds) |

## Project Structure

```
├── config/
│   ├── backends.yaml           # Router backend configuration
│   └── backends.yaml.example   # Example configuration
├── src/mcp_server/
│   ├── server.py               # Server factory & router
│   ├── config.py               # Server & router config
│   ├── routing/                # Routing module
│   │   ├── client.py           # HTTP client for backends
│   │   ├── backends.py         # Backend manager
│   │   ├── engine.py           # Routing engine (strategies)
│   │   ├── health.py           # Health checker & circuit breaker
│   │   ├── models.py           # Data models
│   │   ├── config_loader.py    # YAML config parsing
│   │   └── exceptions.py       # Routing exceptions
│   ├── tools/                  # Tool implementations
│   ├── resources/              # Resource implementations
│   └── prompts/                # Prompt implementations
├── tests/
│   ├── test_routing/           # Routing tests (50+)
│   │   ├── test_models.py      # Data model tests
│   │   ├── test_config_loader.py # Config parsing tests
│   │   ├── test_client.py      # HTTP client tests
│   │   ├── test_engine.py      # Routing strategy tests
│   │   └── test_health.py      # Circuit breaker tests
│   └── fixtures/
│       └── test_backends.yaml  # Test configuration
├── Containerfile               # UBI9 container (podman)
├── Makefile                    # Build targets
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## Running the Router

### Local Development

```bash
# Run with auto-reload
make run-dev

# Run production mode
make run
```

### Container Deployment

```bash
# Build container
make build

# Run container
make run-container

# Or manually:
podman build -t mcp-router:latest .
podman run --rm -p 8000:8000 -v $(pwd)/config:/app/config mcp-router:latest
```

## Testing

The project includes comprehensive tests covering all routing functionality:

```bash
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file
uv run pytest tests/test_routing/test_engine.py -v

# Run routing tests only
uv run pytest tests/test_routing/ -v
```

**Test Coverage:**
- 50+ tests across all routing components
- Config parsing (valid/invalid scenarios)
- Circuit breaker state transitions
- Routing strategies (path, capability, fallback)
- Retry logic and exponential backoff
- Error handling and edge cases
- Health checking and recovery
- Backend management and capability discovery

## Make Targets

```bash
make help          # Show all targets
make install       # Install dependencies
make dev           # Install with dev dependencies
make test          # Run tests
make test-cov      # Run tests with coverage
make lint          # Run linting
make format        # Format code
make run           # Run server locally
make run-dev       # Run with auto-reload
make build         # Build container image
make run-container # Run container
make clean         # Clean build artifacts
```

## For AI Agents

This project uses AGENTS.md files as indexes. Before making changes:

1. Read the `AGENTS.md` in the directory you're working in
2. Follow linked documentation in `.agents/docs/`
3. Update docs when patterns are learned or decisions made

See [AGENTS.md](AGENTS.md) for the root index.

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_tools.py -v
```

## Contributing

See [.agents/docs/workflows/contributing.md](.agents/docs/workflows/contributing.md) for guidelines.

## License

Apache License 2.0

