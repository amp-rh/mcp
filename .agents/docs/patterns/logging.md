# Logging Conventions

See @AGENTS.md for project-wide rules.

## Overview

Logging conventions for MCP server development.

## Rules

- MUST NOT use `print()` for operational output
- MUST use structured logging
- SHOULD include context in log messages
- SHOULD use appropriate log levels

## Setup

```python
import logging

logger = logging.getLogger(__name__)
```

## Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: Confirmation that things are working
- **WARNING**: Something unexpected but not critical
- **ERROR**: A serious problem occurred
- **CRITICAL**: Program may not be able to continue

## Patterns

### Tool Logging

```python
@mcp.tool
def process_data(data: str) -> str:
    logger.info("Processing data", extra={"data_length": len(data)})
    try:
        result = do_processing(data)
        logger.debug("Processing complete", extra={"result_length": len(result)})
        return result
    except ProcessingError as e:
        logger.error("Processing failed", extra={"error": str(e)})
        raise
```

### Structured Logging

```python
logger.info(
    "Request processed",
    extra={
        "tool_name": "my_tool",
        "duration_ms": 150,
        "status": "success",
    }
)
```

## Related

- @.agents/docs/patterns/error-handling.md - Logging errors

