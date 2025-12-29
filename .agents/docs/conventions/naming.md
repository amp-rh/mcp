# Naming Conventions

See @AGENTS.md for project-wide rules.

## Overview

Consistent naming conventions for this project.

## Rules

### Files and Modules

- Use `snake_case` for file names: `example_tools.py`
- Use `snake_case` for module names: `mcp_server`
- Test files start with `test_`: `test_tools.py`

### Classes

- Use `PascalCase`: `ServerConfig`, `ToolExecutionError`
- Suffix exceptions with `Error`: `ValidationError`

### Functions and Methods

- Use `snake_case`: `calculate_total`, `get_user_by_id`
- Use verbs for actions: `fetch_data`, `validate_input`
- Use `is_` or `has_` for boolean returns: `is_valid`, `has_permission`

### Variables

- Use `snake_case`: `user_count`, `max_retries`
- Use `UPPER_CASE` for constants: `DEFAULT_PORT`, `MAX_CONNECTIONS`

### MCP Components

- Tools: Use verb phrases describing the action
  - `calculate_sum`, `fetch_weather`, `search_documents`
- Resources: Use noun phrases with URI scheme
  - `config://settings`, `data://users/{id}`
- Prompts: Use descriptive names
  - `code_review`, `summarize_document`

## Examples

```python
DEFAULT_TIMEOUT = 30

@dataclass
class ServerConfig:
    server_name: str
    host_address: str
    port_number: int

class ConfigurationError(Exception):
    pass

def validate_configuration(config: ServerConfig) -> bool:
    ...

@mcp.tool
def fetch_user_profile(user_id: str) -> dict:
    ...
```

## Related

- @.agents/docs/conventions/coding-style.md - Coding style
- @.agents/docs/conventions/project-structure.md - File organization

