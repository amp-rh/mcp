from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass(frozen=True)
class HealthStatus:
    backend_name: str
    is_healthy: bool = True
    last_check: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    circuit_state: CircuitState = CircuitState.CLOSED
    last_error: str | None = None
    failure_timestamps: tuple[datetime, ...] = ()

    def __post_init__(self) -> None:
        if not self.backend_name:
            raise ValueError("Backend name cannot be empty")
        if self.error_count < 0:
            raise ValueError("Error count cannot be negative")

    def with_success(self) -> "HealthStatus":
        return HealthStatus(
            backend_name=self.backend_name,
            is_healthy=True,
            last_check=datetime.now(),
            error_count=0,
            circuit_state=CircuitState.CLOSED,
            last_error=None,
            failure_timestamps=(),
        )

    def with_failure(self, error_message: str) -> "HealthStatus":
        new_timestamps = (*self.failure_timestamps, datetime.now())
        return HealthStatus(
            backend_name=self.backend_name,
            is_healthy=False,
            last_check=datetime.now(),
            error_count=self.error_count + 1,
            circuit_state=self.circuit_state,
            last_error=error_message,
            failure_timestamps=new_timestamps,
        )

    def with_circuit_state(self, state: CircuitState) -> "HealthStatus":
        return HealthStatus(
            backend_name=self.backend_name,
            is_healthy=self.is_healthy,
            last_check=self.last_check,
            error_count=self.error_count,
            circuit_state=state,
            last_error=self.last_error,
            failure_timestamps=self.failure_timestamps,
        )
