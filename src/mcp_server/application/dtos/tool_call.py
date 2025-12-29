from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolCallRequest:
    tool_name: str
    arguments: dict[str, Any]
    strategy: str | None = None

    def __post_init__(self) -> None:
        if not self.tool_name:
            raise ValueError("Tool name cannot be empty")


@dataclass(frozen=True)
class ToolCallResponse:
    result: Any
    backend_name: str
    strategy_used: str
