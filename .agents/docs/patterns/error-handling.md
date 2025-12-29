# Error Handling Patterns

See @AGENTS.md for project-wide rules.

## Overview

Consistent error handling patterns for this project.

## Principles

1. **Be specific** - Catch specific exceptions, not bare `except:`
2. **Fail fast** - Validate inputs early
3. **Preserve context** - Use exception chaining with `from`
4. **Log appropriately** - See @.agents/docs/patterns/logging.md

## Patterns

### Exception Chaining

```python
try:
    result = external_api_call()
except RequestError as e:
    raise ServiceError("Failed to fetch data") from e
```

### Custom Exceptions

```python
class MCPServerError(Exception):
    pass

class ToolExecutionError(MCPServerError):
    pass

class ResourceNotFoundError(MCPServerError):
    pass
```

### Input Validation

```python
def process_data(data: dict) -> Result:
    if not data:
        raise ValidationError("Data cannot be empty")
    # ... process
```

### MCP Tool Error Handling

```python
@mcp.tool
def risky_operation(param: str) -> str:
    try:
        result = perform_operation(param)
        return result
    except OperationError as e:
        raise ToolExecutionError(f"Operation failed: {e}") from e
```

## Related

- @.agents/docs/patterns/logging.md - Logging errors
- @.agents/docs/patterns/typing.md - Type hints for error handling
- @.agents/docs/tooling/pytest.md - Testing error cases

