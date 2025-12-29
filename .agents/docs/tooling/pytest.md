# Testing with pytest

See @AGENTS.md for project-wide rules.

## Overview

This project uses [pytest](https://docs.pytest.org/) for testing with async support via pytest-asyncio.

## Commands

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific file
uv run pytest tests/test_tools.py

# Run specific test
uv run pytest tests/test_tools.py::test_example_tool

# Run with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run only marked tests
uv run pytest -m "not slow"
```

## Configuration

Configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

## Rules

- MUST run tests before committing
- MUST write tests for new functionality (TDD)
- MUST use fixtures from `conftest.py` when available
- MUST use `pytest.mark.asyncio` for async tests (auto mode handles this)

## Async Testing

With `asyncio_mode = "auto"`, async tests are automatically detected:

```python
async def test_async_tool():
    result = await my_async_tool()
    assert result == expected
```

## Related

- @.agents/docs/workflows/testing.md - Testing workflow
- @.agents/docs/patterns/mcp-patterns.md - Testing MCP components

