"""Tests for data models."""


from mcp_server.routing.models import (
    BackendConfig,
    CircuitBreakerConfig,
    HealthCheckConfig,
    HealthStatus,
    RouteConfig,
    RoutingDecision,
)


class TestRouteConfig:
    """Test RouteConfig model."""

    def test_route_config_creation(self):
        """Test creating a route config."""
        route = RouteConfig(
            pattern="*_user",
            strategy="path",
        )
        assert route.pattern == "*_user"
        assert route.strategy == "path"
        assert route.fallback_to is None

    def test_route_config_with_fallback(self):
        """Test creating a route with fallback."""
        route = RouteConfig(
            pattern="analyze_*",
            strategy="fallback",
            fallback_to="analytics-secondary",
        )
        assert route.fallback_to == "analytics-secondary"


class TestBackendConfig:
    """Test BackendConfig model."""

    def test_backend_config_minimal(self):
        """Test creating minimal backend config."""
        backend = BackendConfig(
            name="test",
            url="http://localhost:8001",
            namespace="test",
        )
        assert backend.name == "test"
        assert backend.url == "http://localhost:8001"
        assert backend.namespace == "test"
        assert backend.priority == 10
        assert backend.routes == []

    def test_backend_config_full(self):
        """Test creating full backend config."""
        health_check = HealthCheckConfig(
            enabled=True,
            interval_seconds=30,
            timeout_seconds=5,
        )
        circuit_breaker = CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=60,
        )
        routes = [
            RouteConfig(pattern="*_user", strategy="path"),
        ]

        backend = BackendConfig(
            name="db",
            url="http://localhost:8001",
            namespace="db",
            priority=10,
            routes=routes,
            health_check=health_check,
            circuit_breaker=circuit_breaker,
        )

        assert backend.name == "db"
        assert backend.priority == 10
        assert len(backend.routes) == 1
        assert backend.health_check.enabled is True
        assert backend.circuit_breaker.failure_threshold == 5


class TestHealthStatus:
    """Test HealthStatus model."""

    def test_health_status_default(self):
        """Test default health status."""
        status = HealthStatus(backend_name="test")
        assert status.backend_name == "test"
        assert status.is_healthy is True
        assert status.error_count == 0
        assert status.circuit_state == "CLOSED"
        assert status.last_error is None

    def test_health_status_unhealthy(self):
        """Test unhealthy status."""
        status = HealthStatus(
            backend_name="test",
            is_healthy=False,
            error_count=5,
            circuit_state="OPEN",
            last_error="Connection refused",
        )
        assert status.is_healthy is False
        assert status.error_count == 5
        assert status.circuit_state == "OPEN"
        assert status.last_error == "Connection refused"


class TestRoutingDecision:
    """Test RoutingDecision model."""

    def test_routing_decision_minimal(self):
        """Test minimal routing decision."""
        backend = object()
        decision = RoutingDecision(
            backend=backend,
            reason="Path pattern matched",
        )
        assert decision.backend is backend
        assert decision.reason == "Path pattern matched"
        assert decision.alternatives == []

    def test_routing_decision_full(self):
        """Test full routing decision."""
        backend = object()
        decision = RoutingDecision(
            backend=backend,
            reason="Capability-based selection",
            alternatives=["db", "api"],
            strategy_used="capability",
        )
        assert decision.backend is backend
        assert decision.alternatives == ["db", "api"]
        assert decision.strategy_used == "capability"
