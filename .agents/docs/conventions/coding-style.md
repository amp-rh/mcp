# Coding Style

See @AGENTS.md for project-wide rules.

## Philosophy

Write **clean, self-documenting code**. The code itself should be clear enough that comments are unnecessary.

## Core Principles

### No Comments

Code should explain itself through:
- Descriptive names
- Small, focused functions
- Clear structure
- Type hints

```python
total_price = calculate_subtotal(items) + calculate_tax(items)
```

### Object-Oriented with Dataclasses

Use Python dataclasses for data structures:

```python
from dataclasses import dataclass

@dataclass
class ToolConfig:
    name: str
    enabled: bool = True
    timeout_seconds: int = 30
```

### Small, Focused Classes

Each class should have a single responsibility:

```python
@dataclass
class User:
    id: str
    email: str

class UserService:
    def find_by_id(self, user_id: str) -> User | None: ...
```

### Test-Driven Development (TDD)

Always write tests first:

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Clean up while tests pass

## Dataclass Patterns

### Immutable by Default

```python
@dataclass(frozen=True)
class ServerConfig:
    host: str
    port: int
```

### Factory Methods

```python
@dataclass
class ServerConfig:
    name: str
    host: str
    port: int
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        return cls(
            name=os.getenv("SERVER_NAME", "mcp-server"),
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8000")),
        )
```

## Rules Summary

- MUST NOT include comments (code should self-document)
- MUST use dataclasses for data structures
- MUST keep classes small and focused (single responsibility)
- MUST write tests before implementation (TDD)
- MUST use descriptive names
- SHOULD prefer composition over inheritance
- SHOULD use frozen dataclasses for immutable data
- SHOULD keep functions under 10 lines

## Related

- @.agents/docs/conventions/naming.md - Naming conventions
- @.agents/docs/patterns/typing.md - Type hints
- @.agents/docs/workflows/testing.md - Testing workflow

