"""Data models for routing configuration and state management."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RouteConfig:
    """Configuration for a routing rule."""

    pattern: str  # Glob-style pattern: "*_user", "query*", etc.
    strategy: str  # "path", "capability", or "fallback"
    fallback_to: str | None = None  # Fallback backend name if strategy is "fallback"


@dataclass
class HealthCheckConfig:
    """Configuration for backend health checking."""

    enabled: bool = True
    interval_seconds: int = 30
    timeout_seconds: int = 5
    endpoint: str | None = None  # Custom health endpoint, defaults to /health


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""

    failure_threshold: int = 5  # Failures before opening circuit
    timeout_seconds: int = 60  # Time to wait before attempting recovery
    half_open_attempts: int = 3  # Attempts to make in half-open state


@dataclass
class BackendConfig:
    """Configuration for a single backend MCP server."""

    name: str
    url: str  # HTTP(S) URL to backend MCP server
    namespace: str  # Prefix for exposed tools/resources (e.g., "db", "api")
    priority: int = 10  # Higher priority backends tried first
    routes: list[RouteConfig] = field(default_factory=list)
    health_check: HealthCheckConfig = field(default_factory=HealthCheckConfig)
    circuit_breaker: CircuitBreakerConfig = field(
        default_factory=CircuitBreakerConfig
    )


@dataclass
class HealthStatus:
    """Health status of a backend."""

    backend_name: str
    is_healthy: bool = True
    last_check: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    circuit_state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    last_error: str | None = None
    failure_timestamps: list[datetime] = field(default_factory=list)


@dataclass
class RoutingDecision:
    """Result of a routing decision."""

    backend: Any  # Backend object (type is Backend, but avoiding circular import)
    reason: str  # Why this backend was selected
    alternatives: list[str] = field(
        default_factory=list
    )  # Names of backends that could have been used
    strategy_used: str = ""  # Which strategy was used
