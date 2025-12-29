# Contributing to This Template

See @AGENTS.md for project-wide rules.

## Overview

Guidelines for contributing to the MCP template.

## Getting Started

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/mcp-template.git
cd mcp-template

# Install with dev dependencies
make dev

# Run tests
make test
```

## Adding Features

### Adding a New Tool

1. Create file in `src/mcp_server/tools/`
2. Implement tool with `@mcp.tool` decorator
3. Add tests in `tests/test_tools.py`
4. Update `tools/__init__.py` if needed

### Adding a New Resource

1. Create file in `src/mcp_server/resources/`
2. Implement resource with `@mcp.resource` decorator
3. Add tests in `tests/test_resources.py`
4. Update `resources/__init__.py` if needed

### Adding a New Prompt

1. Create file in `src/mcp_server/prompts/`
2. Implement prompt with `@mcp.prompt` decorator
3. Add tests in `tests/test_prompts.py`
4. Update `prompts/__init__.py` if needed

## Code Quality

- Follow coding style in @.agents/docs/conventions/coding-style.md
- Use type hints on all public functions
- Write tests first (TDD)
- Run `make check` before submitting

## Documentation

- Update AGENTS.md files when adding new directories
- Document new patterns in `.agents/docs/`
- Update README if adding major features

## Related

- @.agents/docs/workflows/pr-process.md - PR workflow
- @.agents/docs/workflows/testing.md - Testing workflow

