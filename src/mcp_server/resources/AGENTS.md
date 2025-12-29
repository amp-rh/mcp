# AGENTS.md - Resources

See @AGENTS.md for project-wide rules.

## Overview

This directory contains MCP resource implementations. Resources are data sources that AI clients can read.

## Documentation

- @.agents/docs/tooling/fastmcp.md - FastMCP basics
- @.agents/docs/patterns/mcp-patterns.md - Resource design patterns
- @.agents/docs/conventions/mcp-structure.md - Module organization

## Structure

```
resources/
├── __init__.py               # Registration function
├── AGENTS.md                 # This file
├── example_resources.py      # Example resource implementations
└── your_resources.py         # Add your resources here
```

## Rules

- MUST use `@mcp.resource(uri)` decorator
- MUST return string data (use JSON for structured data)
- MUST use meaningful URI schemes (e.g., `config://`, `data://`)
- SHOULD use parameterized URIs for dynamic resources

## URI Patterns

- Static: `config://settings` - Fixed resource
- Dynamic: `data://users/{user_id}` - Parameterized resource

## Adding a New Resource

1. Create a new file or add to an existing file
2. Define the resource function with `@mcp.resource(uri)` decorator
3. Import and register in `__init__.py`
4. Add tests in `tests/test_resources.py`

## Example

```python
import json
from fastmcp import FastMCP

def register_my_resources(mcp: FastMCP) -> None:
    @mcp.resource("api://status")
    def get_api_status() -> str:
        return json.dumps({
            "status": "healthy",
            "uptime_seconds": 3600,
        })

    @mcp.resource("data://items/{item_id}")
    def get_item(item_id: str) -> str:
        return json.dumps({"id": item_id, "name": f"Item {item_id}"})
```

## Testing

```python
import json
from mcp_server.resources.example_resources import get_server_info

def test_server_info_returns_valid_json():
    result = get_server_info()
    data = json.loads(result)
    assert "name" in data
```

