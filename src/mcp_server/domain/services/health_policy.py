from datetime import datetime, timedelta

from mcp_server.domain.value_objects import (
    CircuitBreakerSettings,
    CircuitState,
    HealthStatus,
)


def should_open_circuit(
    health_status: HealthStatus,
    settings: CircuitBreakerSettings,
) -> bool:
    return health_status.error_count >= settings.failure_threshold


def should_attempt_half_open(
    health_status: HealthStatus,
    settings: CircuitBreakerSettings,
) -> bool:
    if health_status.circuit_state != CircuitState.OPEN:
        return False

    if not health_status.failure_timestamps:
        return False

    last_failure = health_status.failure_timestamps[-1]
    timeout_passed = datetime.now() - last_failure >= timedelta(
        seconds=settings.timeout_seconds
    )

    return timeout_passed


def should_close_circuit(
    success_count: int,
    settings: CircuitBreakerSettings,
) -> bool:
    return success_count >= settings.half_open_attempts


def is_healthy(health_status: HealthStatus) -> bool:
    return (
        health_status.is_healthy
        and health_status.circuit_state != CircuitState.OPEN
    )
