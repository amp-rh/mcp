# AGENTS.md - Prompts

See @AGENTS.md for project-wide rules.

## Overview

This directory contains MCP prompt implementations. Prompts are reusable templates that AI clients can use.

## Documentation

- @.agents/docs/tooling/fastmcp.md - FastMCP basics
- @.agents/docs/patterns/mcp-patterns.md - Prompt design patterns
- @.agents/docs/conventions/mcp-structure.md - Module organization

## Structure

```
prompts/
├── __init__.py             # Registration function
├── AGENTS.md               # This file
├── example_prompts.py      # Example prompt implementations
└── your_prompts.py         # Add your prompts here
```

## Rules

- MUST use `@mcp.prompt` decorator
- MUST return string containing the prompt text
- MUST use descriptive function names
- SHOULD use parameters for customization
- SHOULD include clear instructions in the prompt text

## Adding a New Prompt

1. Create a new file or add to an existing file
2. Define the prompt function with `@mcp.prompt` decorator
3. Import and register in `__init__.py`
4. Add tests in `tests/test_prompts.py`

## Example

```python
from fastmcp import FastMCP

def register_my_prompts(mcp: FastMCP) -> None:
    @mcp.prompt
    def code_review(code: str, language: str = "python") -> str:
        return f\"\"\"Review this {language} code for:
- Correctness
- Performance
- Best practices

```{language}
{code}
```

Provide specific, actionable feedback.\"\"\"
```

## Testing

```python
from mcp_server.prompts.example_prompts import code_review

def test_code_review_includes_code():
    code = "print('hello')"
    result = code_review(code=code)
    assert code in result
```

