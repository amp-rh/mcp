# Type Hints and Annotations

See @AGENTS.md for project-wide rules.

## Overview

This project uses Python type hints for documentation and static analysis.

## Rules

- MUST add type hints to all public functions
- MUST add type hints to all class attributes
- SHOULD use `typing` module for complex types
- SHOULD use `|` union syntax (Python 3.10+)

## Patterns

### Function Signatures

```python
def process_items(items: list[str], limit: int | None = None) -> dict[str, int]:
    ...
```

### Optional Values

```python
def find_user(user_id: int) -> User | None:
    ...
```

### Type Aliases

```python
from typing import TypeAlias

ToolResult: TypeAlias = str | dict[str, Any]
ResourceData: TypeAlias = dict[str, Any]
```

### Generics

```python
from typing import TypeVar, Generic

T = TypeVar("T")

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
```

### MCP-Specific Types

```python
from fastmcp import FastMCP, Context

@mcp.tool
def my_tool(ctx: Context, param: str) -> str:
    ...
```

## Related

- @.agents/docs/patterns/error-handling.md - Typing exceptions
- @.agents/docs/tooling/ruff.md - Type checking with Ruff

