"""Tests for routing engine."""

import pytest

from mcp_server.routing.engine import RoutingEngine
from mcp_server.routing.exceptions import RoutingError
from mcp_server.routing.models import BackendConfig


class MockBackend:
    """Mock backend for testing."""

    def __init__(self, name, tools=None):
        self.config = BackendConfig(
            name=name,
            url=f"http://localhost:8001",
            namespace=name,
        )
        self.tools = tools or []


class TestRoutingEngine:
    """Test RoutingEngine functionality."""

    def test_engine_initialization(self):
        """Test RoutingEngine initialization."""
        engine = RoutingEngine(
            default_strategy="capability",
            max_retry_attempts=3,
            retry_backoff_multiplier=2.0,
        )
        assert engine.default_strategy == "capability"
        assert engine.max_retry_attempts == 3
        assert engine.retry_backoff_multiplier == 2.0

    @pytest.mark.asyncio
    async def test_route_tool_no_backends(self):
        """Test routing with no available backends."""
        engine = RoutingEngine()

        with pytest.raises(RoutingError, match="No backends available"):
            await engine.route_tool("fetch_user", [])

    @pytest.mark.asyncio
    async def test_route_by_capability_success(self):
        """Test capability-based routing."""
        engine = RoutingEngine(default_strategy="capability")

        backend1 = MockBackend("db", tools=[{"name": "fetch_user"}])
        backend2 = MockBackend("api", tools=[{"name": "get_user"}])

        decision = await engine.route_by_capability(
            "fetch_user",
            [backend1, backend2],
        )

        assert decision.backend.config.name == "db"
        assert decision.strategy_used == "capability"

    @pytest.mark.asyncio
    async def test_route_by_capability_no_match(self):
        """Test capability-based routing with no matching backend."""
        engine = RoutingEngine()

        backend1 = MockBackend("db", tools=[{"name": "fetch_user"}])
        backend2 = MockBackend("api", tools=[{"name": "get_user"}])

        with pytest.raises(RoutingError, match="No backend has capability"):
            await engine.route_by_capability(
                "nonexistent_tool",
                [backend1, backend2],
            )

    @pytest.mark.asyncio
    async def test_route_by_path_success(self):
        """Test path-based routing."""
        engine = RoutingEngine()

        backend1 = BackendConfig(
            name="db",
            url="http://localhost:8001",
            namespace="db",
            routes=[],
        )
        backend1.routes = [
            type("Route", (), {"pattern": "*_user", "strategy": "path"})()
        ]

        backend = MockBackend("db")
        backend.config = backend1

        decision = await engine.route_by_path("fetch_user", [backend])

        assert decision.backend.config.name == "db"
        assert decision.strategy_used == "path"

    @pytest.mark.asyncio
    async def test_route_by_fallback(self):
        """Test fallback-based routing."""
        engine = RoutingEngine()

        backend1 = MockBackend("primary")
        backend2 = MockBackend("secondary")

        decision = await engine.route_by_fallback(
            "test_tool",
            [backend1, backend2],
        )

        assert decision.backend.config.name == "primary"
        assert decision.strategy_used == "fallback"

    @pytest.mark.asyncio
    async def test_call_with_retry_success_first_try(self):
        """Test successful call on first try."""
        engine = RoutingEngine()

        async def mock_func():
            return "success"

        result = await engine.call_with_retry(mock_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_call_with_retry_success_after_failure(self):
        """Test successful call after initial failure."""
        engine = RoutingEngine(max_retry_attempts=3)

        call_count = 0

        async def mock_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Temporary error")
            return "success"

        result = await engine.call_with_retry(mock_func)
        assert result == "success"
        assert call_count == 2
