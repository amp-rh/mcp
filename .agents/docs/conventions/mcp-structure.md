# MCP Module Organization

See @AGENTS.md for project-wide rules.

## Overview

How to organize MCP tools, resources, and prompts in this template.

## Module Pattern

Each MCP component type (tools, resources, prompts) follows the same pattern:

```
component_type/
├── __init__.py           # Registration function
├── AGENTS.md             # Module-specific guidance
├── example_*.py          # Example implementations
└── your_*.py             # Your implementations
```

## Registration Pattern

Each module exports a `register_*()` function:

```python
from fastmcp import FastMCP

def register_tools(mcp: FastMCP) -> None:
    from .example_tools import greet, calculate_sum
    # Tools are registered when imported with decorators
    # Or explicitly: mcp.tool(greet)
```

## Server Integration

The server factory imports and calls all registration functions:

```python
from fastmcp import FastMCP
from mcp_server.config import ServerConfig
from mcp_server.tools import register_tools
from mcp_server.resources import register_resources
from mcp_server.prompts import register_prompts

def create_server(config: ServerConfig | None = None) -> FastMCP:
    config = config or ServerConfig.from_env()
    mcp = FastMCP(config.name)
    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)
    return mcp
```

## Adding New Components

### Adding a Tool

1. Create file in `src/mcp_server/tools/` (e.g., `api_tools.py`)
2. Define tools with `@mcp.tool` decorator
3. Import in `tools/__init__.py`
4. Add tests in `tests/test_tools.py`

### Adding a Resource

1. Create file in `src/mcp_server/resources/`
2. Define resources with `@mcp.resource` decorator
3. Import in `resources/__init__.py`
4. Add tests in `tests/test_resources.py`

### Adding a Prompt

1. Create file in `src/mcp_server/prompts/`
2. Define prompts with `@mcp.prompt` decorator
3. Import in `prompts/__init__.py`
4. Add tests in `tests/test_prompts.py`

## Grouping Related Components

Group related tools in a single file:

```python
@mcp.tool
def list_users() -> list[dict]: ...

@mcp.tool
def get_user(user_id: str) -> dict: ...

@mcp.tool
def create_user(name: str, email: str) -> dict: ...
```

## Related

- @.agents/docs/patterns/mcp-patterns.md - Design patterns
- @.agents/docs/conventions/project-structure.md - Overall structure
- @src/mcp_server/tools/AGENTS.md - Tool guidance
- @src/mcp_server/resources/AGENTS.md - Resource guidance
- @src/mcp_server/prompts/AGENTS.md - Prompt guidance

