# Testing Workflow

See @AGENTS.md for project-wide rules.

## Overview

Test-driven development workflow for this project.

## TDD Cycle

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Clean up while tests pass

## Before Committing

```bash
# Run all tests
make test

# Or with coverage
make test-cov
```

## Test Structure

```
tests/
├── conftest.py         # Shared fixtures
├── test_tools.py       # Tool tests
├── test_resources.py   # Resource tests
└── test_prompts.py     # Prompt tests
```

## Writing Tests

### Tool Tests

```python
import pytest
from mcp_server.tools.example_tools import greet

@pytest.mark.asyncio
async def test_greet_returns_greeting():
    result = greet(name="World")
    assert result == "Hello, World!"

@pytest.mark.asyncio
async def test_greet_with_empty_name():
    result = greet(name="")
    assert "Hello" in result
```

### Resource Tests

```python
from mcp_server.resources.example_resources import get_server_info

def test_server_info_returns_json():
    result = get_server_info()
    data = json.loads(result)
    assert "name" in data
    assert "version" in data
```

### Prompt Tests

```python
from mcp_server.prompts.example_prompts import code_review

def test_code_review_includes_code():
    code = "print('hello')"
    result = code_review(code=code)
    assert code in result
```

## Related

- @.agents/docs/tooling/pytest.md - pytest commands
- @.agents/docs/conventions/coding-style.md - TDD principles

