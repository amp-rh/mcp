from dataclasses import dataclass


@dataclass(frozen=True)
class RoutePattern:
    pattern: str
    strategy: str
    fallback_to: str | None = None

    def __post_init__(self) -> None:
        if not self.pattern:
            raise ValueError("Route pattern cannot be empty")
        if self.strategy not in ("path", "capability", "fallback"):
            raise ValueError(f"Invalid strategy: {self.strategy}")


@dataclass(frozen=True)
class HealthCheckSettings:
    enabled: bool = True
    interval_seconds: int = 30
    timeout_seconds: int = 5
    endpoint: str | None = None

    def __post_init__(self) -> None:
        if self.interval_seconds < 1:
            raise ValueError("Health check interval must be at least 1 second")
        if self.timeout_seconds < 1:
            raise ValueError("Health check timeout must be at least 1 second")


@dataclass(frozen=True)
class CircuitBreakerSettings:
    failure_threshold: int = 5
    timeout_seconds: int = 60
    half_open_attempts: int = 3

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise ValueError("Failure threshold must be at least 1")
        if self.timeout_seconds < 1:
            raise ValueError("Circuit breaker timeout must be at least 1 second")
        if self.half_open_attempts < 1:
            raise ValueError("Half-open attempts must be at least 1")


@dataclass(frozen=True)
class BackendConfig:
    name: str
    url: str
    namespace: str
    priority: int = 10
    routes: tuple[RoutePattern, ...] = ()
    health_check: HealthCheckSettings = HealthCheckSettings()
    circuit_breaker: CircuitBreakerSettings = CircuitBreakerSettings()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Backend name cannot be empty")
        if not self.url:
            raise ValueError("Backend URL cannot be empty")
        if not self.namespace:
            raise ValueError("Backend namespace cannot be empty")
        if self.priority < 0:
            raise ValueError("Backend priority cannot be negative")
