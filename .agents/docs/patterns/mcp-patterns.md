# MCP Design Patterns

See @AGENTS.md for project-wide rules.

## Overview

Patterns for designing high-quality MCP tools, resources, and prompts.

## Tool Design

### Single Responsibility

Each tool should do one thing well:

```python
@mcp.tool
def fetch_user(user_id: str) -> dict:
    ...

@mcp.tool
def update_user(user_id: str, name: str, email: str) -> dict:
    ...
```

### Descriptive Names

Tool names should clearly indicate their purpose:

```python
@mcp.tool
def calculate_monthly_revenue(year: int, month: int) -> float:
    ...
```

### Rich Type Hints

Use detailed type hints for better AI understanding:

```python
@mcp.tool
def search_documents(
    query: str,
    limit: int = 10,
    include_archived: bool = False,
) -> list[dict[str, str]]:
    ...
```

### Context Usage

Use Context for accessing MCP features:

```python
from fastmcp import Context

@mcp.tool
async def advanced_tool(ctx: Context, param: str) -> str:
    await ctx.info(f"Processing: {param}")
    return result
```

## Resource Design

### URI Patterns

Use meaningful URI schemes:

```python
@mcp.resource("config://app/settings")
def get_app_settings() -> str:
    ...

@mcp.resource("data://users/{user_id}")
def get_user_data(user_id: str) -> str:
    ...
```

### JSON for Structured Data

Return JSON for complex data:

```python
import json

@mcp.resource("api://status")
def get_api_status() -> str:
    return json.dumps({
        "status": "healthy",
        "version": "1.0.0",
        "uptime_seconds": 3600,
    })
```

## Prompt Design

### Parameterized Prompts

Use parameters for flexibility:

```python
@mcp.prompt
def code_review(
    code: str,
    language: str = "python",
    focus: str = "general",
) -> str:
    return f"""Review this {language} code with focus on {focus}:

```{language}
{code}
```

Provide specific, actionable feedback."""
```

### Clear Instructions

Include clear instructions in prompts:

```python
@mcp.prompt
def summarize_document(document: str, max_length: int = 200) -> str:
    return f"""Summarize the following document in {max_length} words or less.

Focus on key points and actionable insights.

Document:
{document}"""
```

## Module Registration

### Registration Functions

Each module exports a registration function:

```python
def register_tools(mcp: FastMCP) -> None:
    from .example_tools import example_tool
    mcp.tool(example_tool)
```

### Lazy Loading

Register tools lazily for better startup:

```python
def register_tools(mcp: FastMCP) -> None:
    @mcp.tool
    def tool_a(): ...
    
    @mcp.tool
    def tool_b(): ...
```

## Related

- @.agents/docs/conventions/mcp-structure.md - Module organization
- @.agents/docs/tooling/fastmcp.md - FastMCP basics
- @src/mcp_server/tools/AGENTS.md - Tool implementation
- @src/mcp_server/resources/AGENTS.md - Resource implementation
- @src/mcp_server/prompts/AGENTS.md - Prompt implementation

