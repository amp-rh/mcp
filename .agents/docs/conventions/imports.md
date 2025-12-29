# Import Organization

See @AGENTS.md for project-wide rules.

## Overview

Import organization conventions enforced by Ruff (isort).

## Order

Imports should be organized in this order:

1. **Standard library** - `import os`, `from datetime import datetime`
2. **Third-party** - `from fastmcp import FastMCP`
3. **First-party** - `from mcp_server.config import ServerConfig`

Each group separated by a blank line.

## Example

```python
import json
import os
from dataclasses import dataclass
from typing import Any

from fastmcp import FastMCP

from mcp_server.config import ServerConfig
from mcp_server.tools import register_tools
```

## Rules

- MUST separate import groups with blank lines
- MUST use absolute imports for first-party code
- SHOULD use `from x import y` for specific imports
- SHOULD NOT use wildcard imports (`from x import *`)

## Ruff Configuration

```toml
[tool.ruff.lint.isort]
known-first-party = ["mcp_server"]
```

## Common Patterns

### Type Checking Imports

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp_server.models import User
```

### Re-exports in __init__.py

```python
from mcp_server.tools.example_tools import example_tool

__all__ = ["example_tool"]
```

## Related

- @.agents/docs/tooling/ruff.md - Ruff configuration

