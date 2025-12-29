"""Core routing logic and strategy implementations."""

import asyncio
import fnmatch
import logging
from collections.abc import Callable
from typing import Any

from mcp_server.routing.exceptions import (
    BackendTimeoutError,
    RoutingError,
)
from mcp_server.routing.models import RoutingDecision

logger = logging.getLogger(__name__)


class RoutingEngine:
    """Implements routing strategies and retry logic."""

    def __init__(
        self,
        default_strategy: str = "capability",
        max_retry_attempts: int = 3,
        retry_backoff_multiplier: float = 2.0,
        max_retry_backoff: int = 10,
    ):
        """Initialize routing engine.

        Args:
            default_strategy: Default routing strategy if no route matches
            max_retry_attempts: Maximum number of retry attempts
            retry_backoff_multiplier: Multiplier for exponential backoff
            max_retry_backoff: Maximum backoff time in seconds
        """
        self.default_strategy = default_strategy
        self.max_retry_attempts = max_retry_attempts
        self.retry_backoff_multiplier = retry_backoff_multiplier
        self.max_retry_backoff = max_retry_backoff

    async def route_tool(
        self,
        tool_name: str,
        backends: list[Any],
        strategy: str | None = None,
    ) -> RoutingDecision:
        """Route a tool call to an appropriate backend.

        Args:
            tool_name: Name of the tool
            backends: List of available backends
            strategy: Routing strategy to use (uses default if None)

        Returns:
            RoutingDecision with selected backend

        Raises:
            RoutingError: If no suitable backend is found
        """
        if not backends:
            raise RoutingError(f"No backends available to route tool: {tool_name}")

        strategy = strategy or self.default_strategy
        logger.debug(f"Routing tool {tool_name} using strategy: {strategy}")

        if strategy == "path":
            return await self.route_by_path(tool_name, backends)
        elif strategy == "capability":
            return await self.route_by_capability(tool_name, backends)
        elif strategy == "fallback":
            return await self.route_by_fallback(tool_name, backends)
        else:
            raise RoutingError(f"Unknown routing strategy: {strategy}")

    async def route_by_path(
        self,
        tool_name: str,
        backends: list[Any],
    ) -> RoutingDecision:
        """Route based on tool name pattern matching.

        Args:
            tool_name: Name of the tool
            backends: List of available backends

        Returns:
            RoutingDecision with selected backend

        Raises:
            RoutingError: If no backend pattern matches
        """
        logger.debug(f"Path-based routing for tool: {tool_name}")

        # Find backends with matching route patterns
        candidates = []
        for backend in backends:
            for route in backend.config.routes:
                if fnmatch.fnmatch(tool_name, route.pattern):
                    candidates.append((backend, route.pattern))
                    break

        if not candidates:
            raise RoutingError(
                f"No path-based route found for tool: {tool_name}",
                routing_decision={
                    "strategy": "path",
                    "tool": tool_name,
                    "available_backends": [b.config.name for b in backends],
                },
            )

        # Sort by backend priority and return highest priority
        candidates.sort(
            key=lambda x: x[0].config.priority,
        )
        selected_backend = candidates[0][0]
        pattern = candidates[0][1]

        logger.info(
            f"Path-based routing selected {selected_backend.config.name} "
            f"for tool {tool_name} (pattern: {pattern})"
        )

        return RoutingDecision(
            backend=selected_backend,
            reason=f"Matched path pattern '{pattern}'",
            alternatives=[c[0].config.name for c in candidates[1:]],
            strategy_used="path",
        )

    async def route_by_capability(
        self,
        tool_name: str,
        backends: list[Any],
    ) -> RoutingDecision:
        """Route based on backend capabilities.

        Args:
            tool_name: Name of the tool
            backends: List of available backends

        Returns:
            RoutingDecision with selected backend

        Raises:
            RoutingError: If no backend has the capability
        """
        logger.debug(f"Capability-based routing for tool: {tool_name}")

        # Find backends that have this tool
        candidates = []
        for backend in sorted(backends, key=lambda b: b.config.priority):
            if any(t.get("name") == tool_name for t in backend.tools):
                candidates.append(backend)

        if not candidates:
            raise RoutingError(
                f"No backend has capability for tool: {tool_name}",
                routing_decision={
                    "strategy": "capability",
                    "tool": tool_name,
                    "available_backends": [b.config.name for b in backends],
                },
            )

        selected_backend = candidates[0]
        logger.info(
            f"Capability-based routing selected {selected_backend.config.name} "
            f"for tool {tool_name}"
        )

        return RoutingDecision(
            backend=selected_backend,
            reason="Backend has the required tool capability",
            alternatives=[c.config.name for c in candidates[1:]],
            strategy_used="capability",
        )

    async def route_by_fallback(
        self,
        tool_name: str,
        backends: list[Any],
    ) -> RoutingDecision:
        """Route using priority/fallback chain.

        Args:
            tool_name: Name of the tool
            backends: List of available backends (ordered by priority)

        Returns:
            RoutingDecision with selected backend

        Raises:
            RoutingError: If no healthy backends in chain
        """
        logger.debug(f"Fallback-based routing for tool: {tool_name}")

        # Try backends in priority order, skipping unhealthy ones
        for backend in backends:
            logger.debug(f"Trying fallback backend: {backend.config.name}")
            # Fallback routing doesn't check if tool exists, tries backend
            return RoutingDecision(
                backend=backend,
                reason=f"Using fallback chain (priority: {backend.config.priority})",
                alternatives=[b.config.name for b in backends[1:]],
                strategy_used="fallback",
            )

        raise RoutingError(
            f"No backends available for fallback routing: {tool_name}",
            routing_decision={
                "strategy": "fallback",
                "tool": tool_name,
                "available_backends": [b.config.name for b in backends],
            },
        )

    async def call_with_retry(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute a function with exponential backoff retry logic.

        Args:
            func: Async function to call
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            BackendTimeoutError: If all retries timeout
            Exception: If all retries fail with non-timeout error
        """
        last_error = None
        backoff_time = 1.0

        for attempt in range(self.max_retry_attempts):
            try:
                logger.debug(f"Attempt {attempt + 1}/{self.max_retry_attempts}")
                result = await func(*args, **kwargs)
                if attempt > 0:
                    logger.debug(f"Succeeded on retry {attempt}")
                return result

            except TimeoutError as e:
                last_error = BackendTimeoutError(
                    f"Request timed out on attempt {attempt + 1}",
                    original_error=e,
                )
                logger.debug(f"Timeout on attempt {attempt + 1}")

                if attempt < self.max_retry_attempts - 1:
                    sleep_time = min(backoff_time, self.max_retry_backoff)
                    logger.debug(f"Retrying after {sleep_time}s")
                    await asyncio.sleep(sleep_time)
                    backoff_time *= self.retry_backoff_multiplier

            except Exception as e:
                last_error = e
                logger.debug(f"Error on attempt {attempt + 1}: {e}")

                if attempt < self.max_retry_attempts - 1:
                    sleep_time = min(backoff_time, self.max_retry_backoff)
                    logger.debug(f"Retrying after {sleep_time}s")
                    await asyncio.sleep(sleep_time)
                    backoff_time *= self.retry_backoff_multiplier

        if isinstance(last_error, BackendTimeoutError):
            raise last_error

        raise last_error or Exception("Unknown error during retry")
