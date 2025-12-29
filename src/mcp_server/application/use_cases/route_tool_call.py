import asyncio
from typing import Any

from mcp_server.application.dtos import ToolCallRequest, ToolCallResponse
from mcp_server.application.ports import MCPClientPort
from mcp_server.domain.exceptions import BackendNotFoundError
from mcp_server.domain.repositories import BackendRepository
from mcp_server.domain.services import (
    route_by_capability,
    route_by_fallback,
    route_by_path,
)


class RouteToolCall:
    def __init__(
        self,
        backend_repository: BackendRepository,
        client_factory: dict[str, MCPClientPort],
        max_retry_attempts: int = 3,
        retry_backoff_multiplier: float = 2.0,
        max_retry_backoff: int = 10,
    ) -> None:
        self.backend_repository = backend_repository
        self.client_factory = client_factory
        self.max_retry_attempts = max_retry_attempts
        self.retry_backoff_multiplier = retry_backoff_multiplier
        self.max_retry_backoff = max_retry_backoff

    async def execute(self, request: ToolCallRequest) -> ToolCallResponse:
        backends = self.backend_repository.get_with_tool(request.tool_name)

        strategy = request.strategy or "capability"
        if strategy == "capability":
            decision = route_by_capability(request.tool_name, backends)
        elif strategy == "path":
            decision = route_by_path(request.tool_name, backends)
        elif strategy == "fallback":
            decision = route_by_fallback(request.tool_name, backends)
        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")

        backend = self.backend_repository.get(decision.backend_name)
        if not backend:
            raise BackendNotFoundError(decision.backend_name)

        backend.ensure_available()

        client = self.client_factory.get(backend.name)
        if not client:
            raise BackendNotFoundError(backend.name)

        result = await self._call_with_retry(
            client.call_tool,
            request.tool_name,
            request.arguments,
            backend.name,
        )

        backend.record_success()

        return ToolCallResponse(
            result=result,
            backend_name=backend.name,
            strategy_used=decision.strategy_used,
        )

    async def _call_with_retry(
        self,
        func: Any,
        tool_name: str,
        arguments: dict[str, Any],
        backend_name: str,
    ) -> Any:
        last_error = None
        backoff_time = 1.0

        for attempt in range(self.max_retry_attempts):
            try:
                result = await func(tool_name, arguments)
                return result

            except Exception as e:
                last_error = e
                backend = self.backend_repository.get(backend_name)
                if backend:
                    backend.record_failure(str(e))

                if attempt < self.max_retry_attempts - 1:
                    sleep_time = min(backoff_time, self.max_retry_backoff)
                    await asyncio.sleep(sleep_time)
                    backoff_time *= self.retry_backoff_multiplier

        raise last_error or Exception("Unknown error during retry")
