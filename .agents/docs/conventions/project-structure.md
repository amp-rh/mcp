# Project Structure

See @AGENTS.md for project-wide rules.

## Overview

Standard project layout for this MCP server template.

## Structure

```
project-root/
├── AGENTS.md               # Root agent index
├── README.md               # Project documentation
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lock file
├── Makefile                # Build targets
├── Containerfile           # Container definition (podman)
├── .agents/                # Agent documentation
│   └── docs/
│       ├── tooling/
│       ├── patterns/
│       ├── conventions/
│       ├── workflows/
│       └── architecture/
├── src/
│   ├── AGENTS.md           # Source code index
│   └── mcp_server/         # Main package
│       ├── __init__.py
│       ├── server.py       # Server factory
│       ├── config.py       # Configuration
│       ├── tools/          # Tool implementations
│       ├── resources/      # Resource implementations
│       └── prompts/        # Prompt implementations
└── tests/
    ├── AGENTS.md           # Test index
    ├── conftest.py         # Shared fixtures
    └── test_*.py           # Test modules
```

## Rules

- MUST place source code under `src/`
- MUST place tests under `tests/`
- MUST place agent documentation under `.agents/docs/`
- MUST have AGENTS.md in directories where agents will work

## Module Organization

### Single Responsibility

Each module should have a clear, single purpose:

- `server.py` - Server factory and setup
- `config.py` - Configuration dataclass
- `tools/` - MCP tool implementations
- `resources/` - MCP resource implementations
- `prompts/` - MCP prompt implementations

### Package Growth

When a module grows large, convert to a package:

```
tools/
├── __init__.py         # Registration function
├── AGENTS.md           # Module guidance
├── data_tools.py       # Data-related tools
└── api_tools.py        # API-related tools
```

## Related

- @.agents/docs/conventions/naming.md - File naming conventions
- @.agents/docs/conventions/mcp-structure.md - MCP module organization
- @src/AGENTS.md - Source code guidance
- @tests/AGENTS.md - Test organization

