# FastMCP Server Development

See @AGENTS.md for project-wide rules.

## Overview

This project uses [FastMCP](https://gofastmcp.com) to build MCP (Model Context Protocol) servers that expose tools, resources, and prompts to AI clients.

## Running the Server

```bash
# Run with HTTP/SSE transport (production)
uv run fastmcp run src/mcp_server/server.py:mcp --transport sse --port 8000

# Run with auto-reload (development)
uv run fastmcp dev src/mcp_server/server.py:mcp --transport sse --port 8000

# Run with stdio transport (for CLI integration)
uv run fastmcp run src/mcp_server/server.py:mcp --transport stdio
```

## Core Concepts

### Tools
Functions that AI can call to perform actions:

```python
from fastmcp import FastMCP

mcp = FastMCP("my-server")

@mcp.tool
def calculate_sum(a: int, b: int) -> int:
    return a + b
```

### Resources
Data sources that AI can read:

```python
@mcp.resource("config://settings")
def get_settings() -> str:
    return json.dumps({"key": "value"})
```

### Prompts
Reusable prompt templates:

```python
@mcp.prompt
def code_review(code: str) -> str:
    return f"Review this code:\n\n{code}"
```

## Project Structure

This template organizes MCP components into modules:

```
src/mcp_server/
├── server.py           # Server factory
├── config.py           # Configuration
├── tools/              # Tool implementations
├── resources/          # Resource implementations
└── prompts/            # Prompt implementations
```

## Testing

Use pytest with async support:

```python
import pytest
from mcp_server.tools.example_tools import example_tool

@pytest.mark.asyncio
async def test_example_tool():
    result = await example_tool(param="value")
    assert result == expected
```

## Related

- @.agents/docs/patterns/mcp-patterns.md - MCP design patterns
- @.agents/docs/conventions/mcp-structure.md - Module organization
- [FastMCP Documentation](https://gofastmcp.com)

