# AGENTS.md - Tools

See @AGENTS.md for project-wide rules.

## Overview

This directory contains MCP tool implementations. Tools are functions that AI clients can call to perform actions.

## Documentation

- @.agents/docs/tooling/fastmcp.md - FastMCP basics
- @.agents/docs/patterns/mcp-patterns.md - Tool design patterns
- @.agents/docs/conventions/mcp-structure.md - Module organization

## Structure

```
tools/
├── __init__.py           # Registration function
├── AGENTS.md             # This file
├── example_tools.py      # Example tool implementations
└── your_tools.py         # Add your tools here
```

## Rules

- MUST use `@mcp.tool` decorator or register via `mcp.tool(func)`
- MUST include type hints on all parameters and return types
- MUST use descriptive function names that indicate the action
- SHOULD include docstrings for complex tools (AI uses these)
- SHOULD handle errors gracefully and return meaningful messages

## Adding a New Tool

1. Create a new file or add to an existing file
2. Define the tool function with `@mcp.tool` decorator
3. Import and register in `__init__.py`
4. Add tests in `tests/test_tools.py`

## Example

```python
from fastmcp import FastMCP

def register_my_tools(mcp: FastMCP) -> None:
    @mcp.tool
    def fetch_data(source: str, limit: int = 10) -> list[dict]:
        """Fetch data from the specified source."""
        return [{"id": i, "source": source} for i in range(limit)]
```

## Testing

```python
from mcp_server.tools.example_tools import greet

def test_greet():
    result = greet(name="World")
    assert result == "Hello, World!"
```

