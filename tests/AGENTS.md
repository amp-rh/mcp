# AGENTS.md - Tests

See @AGENTS.md for project-wide rules.

## Documentation

### Testing

- @.agents/docs/tooling/pytest.md - pytest commands and configuration
- @.agents/docs/workflows/testing.md - Testing workflow and requirements

### Patterns

- @.agents/docs/patterns/error-handling.md - Testing error cases
- @.agents/docs/patterns/mcp-patterns.md - Testing MCP components

## Rules

- MUST name test files `test_*.py`
- MUST name test functions `test_*`
- MUST use fixtures from `conftest.py` when available
- MUST run `uv run pytest` before committing

## Structure

```
tests/
├── AGENTS.md           # This file
├── __init__.py         # Package marker
├── conftest.py         # Shared fixtures
├── test_tools.py       # Tool tests
├── test_resources.py   # Resource tests
└── test_prompts.py     # Prompt tests
```

## Fixtures

Shared fixtures are defined in `conftest.py`. Check there first before creating test-specific setup.

Available fixtures:
- `mcp_server` - Configured FastMCP server instance

## Running Tests

```bash
# All tests
uv run pytest

# Verbose
uv run pytest -v

# Specific file
uv run pytest tests/test_tools.py

# With coverage
uv run pytest --cov=src
```

## Testing MCP Components

### Testing Tools

```python
def test_greet_returns_greeting():
    result = greet(name="World")
    assert result == "Hello, World!"
```

### Testing Resources

```python
def test_server_info_returns_json():
    result = get_server_info()
    data = json.loads(result)
    assert "name" in data
```

### Testing Prompts

```python
def test_code_review_includes_code():
    code = "print('hello')"
    result = code_review(code=code)
    assert code in result
```

