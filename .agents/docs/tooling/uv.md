# Package Management with uv

See @AGENTS.md for project-wide rules.

## Overview

This project uses [uv](https://github.com/astral-sh/uv) for Python package management.

## Commands

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev

# Add a dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Run a command in the virtual environment
uv run python script.py
uv run pytest
```

## Rules

- MUST run `uv sync` after cloning the repository
- MUST run `uv sync` after modifying `pyproject.toml`
- MUST use `uv run` to execute commands in the virtual environment
- MUST NOT manually edit `uv.lock`

## Adding Dependencies

When adding a new dependency:

1. Add to `pyproject.toml` under `[project.dependencies]` or `[project.optional-dependencies.dev]`
2. Run `uv sync`
3. Document the dependency purpose in this file if non-obvious

## Current Dependencies

### Runtime
- `fastmcp>=2.0.0` - MCP server framework

### Development
- `pytest>=8.0.0` - Testing framework
- `pytest-cov>=4.0.0` - Coverage reporting
- `pytest-asyncio>=0.23.0` - Async test support
- `ruff>=0.4.0` - Linting and formatting

