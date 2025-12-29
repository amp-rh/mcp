# Linting and Formatting with Ruff

See @AGENTS.md for project-wide rules.

## Overview

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

## Commands

```bash
# Check for issues
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

## Configuration

Configuration is in `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # Pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
]
```

## Rules

- MUST run `ruff check .` before committing
- MUST fix all linting errors before committing
- SHOULD run `ruff format .` to maintain consistent style

## Common Issues

### Import Sorting (I001)
Imports not sorted correctly. Fix with `ruff check --fix .`

### Unused Imports (F401)
Remove unused imports or add `# noqa: F401` if re-exporting.

### Line Too Long (E501)
Break long lines. Max line length is 88 characters.

