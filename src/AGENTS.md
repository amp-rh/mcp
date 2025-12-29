# AGENTS.md - Source Code

See @AGENTS.md for project-wide rules.

## Documentation

### Patterns

- @.agents/docs/patterns/error-handling.md - Error handling patterns
- @.agents/docs/patterns/typing.md - Type hints and annotations
- @.agents/docs/patterns/logging.md - Logging conventions
- @.agents/docs/patterns/mcp-patterns.md - MCP design patterns

### Conventions

- @.agents/docs/conventions/naming.md - Naming conventions
- @.agents/docs/conventions/imports.md - Import organization
- @.agents/docs/conventions/project-structure.md - Module organization
- @.agents/docs/conventions/mcp-structure.md - MCP component organization

### Tooling

- @.agents/docs/tooling/ruff.md - Linting and formatting
- @.agents/docs/tooling/fastmcp.md - FastMCP development

## Rules

- MUST follow coding style in @.agents/docs/conventions/coding-style.md
- MUST use type hints on all public functions
- MUST use dataclasses for data structures
- MUST write tests first (TDD)
- MUST NOT include comments (code should self-document)
- MUST NOT use `print()` for operational output (use logging)
- MUST follow naming conventions in @.agents/docs/conventions/naming.md

## Structure

```
src/
├── AGENTS.md                   # This file
├── __init__.py                 # Package root
└── mcp_server/                 # Main MCP server package
    ├── __init__.py             # Package init with version
    ├── server.py               # Server factory
    ├── config.py               # Configuration dataclass
    ├── tools/                  # Tool implementations
    │   └── AGENTS.md           # Tool guidance
    ├── resources/              # Resource implementations
    │   └── AGENTS.md           # Resource guidance
    └── prompts/                # Prompt implementations
        └── AGENTS.md           # Prompt guidance
```

## Adding Components

See @.agents/docs/conventions/mcp-structure.md for how to add new tools, resources, or prompts.

