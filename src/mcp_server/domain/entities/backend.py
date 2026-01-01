from dataclasses import dataclass, field
from typing import Any

from mcp_server.domain.exceptions import CircuitBreakerOpenError
from mcp_server.domain.value_objects import (
    BackendConfig,
    CircuitState,
    HealthStatus,
)


@dataclass
class Backend:
    config: BackendConfig
    health_status: HealthStatus = field(init=False)
    tools: list[dict[str, Any]] = field(default_factory=list)
    resources: list[dict[str, Any]] = field(default_factory=list)
    prompts: list[dict[str, Any]] = field(default_factory=list)
    process_id: int | None = None

    def __post_init__(self) -> None:
        self.health_status = HealthStatus(backend_name=self.config.name)

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def is_healthy(self) -> bool:
        return self.health_status.is_healthy and not self.is_circuit_open

    @property
    def is_circuit_open(self) -> bool:
        return self.health_status.circuit_state == CircuitState.OPEN

    @property
    def is_managed_process(self) -> bool:
        return self.config.source.process_config is not None

    @property
    def is_running(self) -> bool:
        return self.process_id is not None

    def has_tool(self, tool_name: str) -> bool:
        return any(t.get("name") == tool_name for t in self.tools)

    def has_resource(self, resource_uri: str) -> bool:
        return any(r.get("uri") == resource_uri for r in self.resources)

    def has_prompt(self, prompt_name: str) -> bool:
        return any(p.get("name") == prompt_name for p in self.prompts)

    def record_success(self) -> None:
        self.health_status = self.health_status.with_success()

    def record_failure(self, error_message: str) -> None:
        self.health_status = self.health_status.with_failure(error_message)

        threshold = self.config.circuit_breaker.failure_threshold
        if self.health_status.error_count >= threshold:
            self.open_circuit()

    def open_circuit(self) -> None:
        self.health_status = self.health_status.with_circuit_state(CircuitState.OPEN)

    def close_circuit(self) -> None:
        self.health_status = self.health_status.with_circuit_state(CircuitState.CLOSED)

    def half_open_circuit(self) -> None:
        self.health_status = self.health_status.with_circuit_state(
            CircuitState.HALF_OPEN
        )

    def ensure_available(self) -> None:
        if self.is_circuit_open:
            raise CircuitBreakerOpenError(self.name)

    def update_capabilities(
        self,
        tools: list[dict[str, Any]],
        resources: list[dict[str, Any]],
        prompts: list[dict[str, Any]],
    ) -> None:
        self.tools = tools
        self.resources = resources
        self.prompts = prompts
