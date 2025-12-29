# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server template built with FastMCP. It provides a production-ready foundation for building AI-ready servers with organized modules for tools, resources, and prompts. The project includes HTTP/SSE transport support, container deployment, and comprehensive agent documentation.

## Development Commands

### Build & Dependencies

```bash
make install       # Install runtime dependencies with uv
make dev          # Install with dev dependencies (pytest, ruff, etc.)
```

### Development & Testing

```bash
make run          # Run MCP server locally on port 8000 (HTTP/SSE)
make run-dev      # Run server with auto-reload for development
make test         # Run all tests
make test-cov     # Run tests with coverage report
uv run pytest tests/test_tools.py -v     # Run single test file
```

### Code Quality

```bash
make lint         # Check code with ruff (E, W, F, I, B, C4, UP rules)
make format       # Format code and apply auto-fixes with ruff
make check        # Run both lint and test
```

### Container & Cleanup

```bash
make build        # Build podman container image
make run-container # Run container on port 8000
make clean        # Remove build artifacts and cache
```

## Architecture

### Server Structure

The server is built with FastMCP and organized into clear modules:

- **`src/mcp_server/server.py`** - Server factory that instantiates FastMCP and registers all components
- **`src/mcp_server/config.py`** - Configuration dataclass, loads from environment variables
- **`src/mcp_server/tools/`** - MCP tool implementations (functions AI can call)
- **`src/mcp_server/resources/`** - MCP resource implementations (data sources AI can read)
- **`src/mcp_server/prompts/`** - MCP prompt implementations (reusable prompt templates)

Each module has a `register_*()` function that the server factory calls to register components.

### MCP Components

**Tools** - Functions that perform actions:
```python
@mcp.tool
def fetch_user(user_id: str) -> dict:
    """Get user by ID."""
    return {"id": user_id, "name": "User"}
```

**Resources** - Read-only data sources with URI-based access:
```python
@mcp.resource("api://users/{user_id}")
def get_user(user_id: str) -> str:
    return json.dumps({"id": user_id})
```

**Prompts** - Parameterized prompt templates:
```python
@mcp.prompt
def analyze(data: str, focus: str = "trends") -> str:
    return f"Analyze this data focusing on {focus}:\n\n{data}"
```

### Configuration

Configuration uses environment variables:
- `MCP_SERVER_NAME` - Server name (default: `mcp-server`)
- `MCP_HOST` - Bind address (default: `0.0.0.0`)
- `MCP_PORT` - Listen port (default: `8000`)

## Key Patterns & Conventions

### Project Documentation System

This project uses **AGENTS.md files** as hierarchical documentation indexes. Always read the AGENTS.md in your working directory:

- Root: `/AGENTS.md` - Project-wide rules and index
- Source: `/src/AGENTS.md` - Source code guidance
- Agent docs: `/.agents/docs/` - Detailed patterns and conventions
  - `patterns/` - Error handling, typing, logging, MCP patterns
  - `conventions/` - Naming, imports, structure, MCP organization
  - `tooling/` - uv, pytest, ruff, fastmcp
  - `workflows/` - PR, testing, release processes
  - `architecture/` - Design decisions

### Testing

- Tests use **pytest** with async support (`pytest-asyncio`)
- Test configuration in `pyproject.toml` sets `pythonpath = ["src"]`
- Tests are in `tests/` directory with fixtures in `conftest.py`
- Coverage tracking enabled (branch coverage)

### Code Quality

**ruff** is used for linting and formatting:
- Rule sets: E, W, F, I (imports), B, C4 (comprehensions), UP (pyupgrade)
- Line length: 88 characters
- Target: Python 3.11+

### Dependencies

Use **uv** for dependency management (not pip):
```bash
uv add <package>           # Add a dependency
uv add --dev <package>     # Add dev dependency
uv sync                    # Install from lock file
```

## Important Rules

1. **MUST read AGENTS.md** before modifying files in any directory
2. **MUST run `uv sync`** after modifying `pyproject.toml`
3. **MUST run `pytest`** before committing changes
4. **MUST NOT add dependencies** without documenting in `/.agents/docs/tooling/uv.md`
5. **MUST follow MCP patterns** documented in `/.agents/docs/patterns/mcp-patterns.md`

## Adding New Components

### Adding a Tool

Create a file in `src/mcp_server/tools/`:
```python
def register_my_tools(mcp: FastMCP) -> None:
    @mcp.tool
    def fetch_weather(city: str) -> dict:
        """Fetch weather for a city."""
        return {"city": city, "temp": 72}
```

Import and register in `tools/__init__.py`.

### Adding a Resource

Create a file in `src/mcp_server/resources/`:
```python
def register_my_resources(mcp: FastMCP) -> None:
    @mcp.resource("api://weather/{city}")
    def get_weather(city: str) -> str:
        return json.dumps({"city": city, "temp": 72})
```

### Adding a Prompt

Create a file in `src/mcp_server/prompts/`:
```python
def register_my_prompts(mcp: FastMCP) -> None:
    @mcp.prompt
    def analyze_code(code: str, language: str = "python") -> str:
        return f"Review this {language}:\n\n{code}"
```

## Container Deployment

The project uses **podman** and UBI9 for enterprise-ready containerization:

```bash
make build              # Build: podman build -t mcp-template:latest .
make run-container      # Run: podman run --rm -p 8000:8000 mcp-template:latest
```

The container runs as a rootless user for security.

## For More Information

- **MCP Protocol Details**: See `/.agents/docs/patterns/mcp-patterns.md`
- **FastMCP Guide**: See `/.agents/docs/tooling/fastmcp.md`
- **Testing Details**: See `/.agents/docs/workflows/testing.md`
- **PR Process**: See `/.agents/docs/workflows/pr-process.md`
- **Full Project Index**: See `AGENTS.md`
