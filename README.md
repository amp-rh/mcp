# MCP Server Template

A production-ready FastMCP server template with organized tools, resources, and prompts. Built with the AGENTS.md documentation system for AI agent guidance.

## Features

- **Modular Architecture**: Organized modules for tools, resources, and prompts
- **FastMCP**: High-level Python framework for MCP servers
- **HTTP/SSE Transport**: Ready for web deployment
- **Container Support**: UBI9 rootless container for enterprise deployments
- **AGENTS.md System**: Hierarchical documentation indexes for AI agents
- **Modern Python Tooling**: uv, pytest, ruff

## Quick Start

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/YOUR-USERNAME/mcp-template.git
cd mcp-template
uv sync --extra dev

# Run tests
make test

# Run the server locally
make run
```

The server will be available at `http://localhost:8000`.

## Project Structure

```
├── AGENTS.md               # AI agent guidance (start here)
├── .agents/                # Agent-specific resources
│   ├── commands/           # Slash command definitions
│   ├── docs/               # Granular documentation
│   │   ├── tooling/        # uv, pytest, ruff, fastmcp
│   │   ├── patterns/       # Code patterns, MCP patterns
│   │   ├── conventions/    # Naming, imports, structure
│   │   ├── workflows/      # PR, testing, releases
│   │   └── architecture/   # Design decisions
│   └── scratch/            # Agent working space
├── src/mcp_server/         # Source code
│   ├── server.py           # Server factory
│   ├── config.py           # Configuration
│   ├── tools/              # Tool implementations
│   ├── resources/          # Resource implementations
│   └── prompts/            # Prompt implementations
├── tests/                  # Test suite
├── Containerfile           # UBI9 container (podman)
├── Makefile                # Build targets
└── pyproject.toml          # Project configuration
```

## Using This Template

### 1. Create Your Project

```bash
# Option A: Use as GitHub template
# Click "Use this template" on GitHub

# Option B: Clone and reinitialize
git clone https://github.com/YOUR-USERNAME/mcp-template.git my-mcp-server
cd my-mcp-server
rm -rf .git
git init
```

### 2. Rename the Package

```bash
# Rename the package directory
mv src/mcp_server src/your_server_name

# Update references in these files:
# - pyproject.toml (name, packages, known-first-party)
# - src/your_server_name/__init__.py
# - All import statements
```

### 3. Add Your Components

#### Adding a Tool

Create a new file in `src/your_server/tools/`:

```python
from fastmcp import FastMCP

def register_my_tools(mcp: FastMCP) -> None:
    @mcp.tool
    def fetch_weather(city: str) -> dict:
        """Fetch weather data for a city."""
        return {"city": city, "temp": 72, "condition": "sunny"}
```

Update `tools/__init__.py` to import and register.

#### Adding a Resource

Create a new file in `src/your_server/resources/`:

```python
import json
from fastmcp import FastMCP

def register_my_resources(mcp: FastMCP) -> None:
    @mcp.resource("api://users/{user_id}")
    def get_user(user_id: str) -> str:
        return json.dumps({"id": user_id, "name": f"User {user_id}"})
```

#### Adding a Prompt

Create a new file in `src/your_server/prompts/`:

```python
from fastmcp import FastMCP

def register_my_prompts(mcp: FastMCP) -> None:
    @mcp.prompt
    def analyze_data(data: str, focus: str = "trends") -> str:
        return f"Analyze this data with focus on {focus}:\n\n{data}"
```

## Running the Server

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
podman build -t mcp-template:latest .
podman run --rm -p 8000:8000 mcp-template:latest
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_NAME` | `mcp-server` | Server name |
| `MCP_HOST` | `0.0.0.0` | Host to bind to |
| `MCP_PORT` | `8000` | Port to listen on |

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

