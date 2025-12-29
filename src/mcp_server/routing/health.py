"""Health checking and circuit breaker pattern implementation."""

import asyncio
import logging
from datetime import datetime, timedelta

from mcp_server.routing.models import HealthStatus

logger = logging.getLogger(__name__)


class HealthChecker:
    """Manages backend health checking with circuit breaker pattern."""

    def __init__(self, check_interval: int = 30):
        """Initialize health checker.

        Args:
            check_interval: Interval in seconds between health checks
        """
        self.check_interval = check_interval
        self.circuit_states = {}
        self.circuit_timeouts = {}
        self.error_counts = {}
        self.last_check_times = {}
        self.failure_timestamps = {}
        self.check_task = None

    async def start(self, backend_manager: "BackendManager") -> None:  # noqa: F821
        """Start background health checking loop.

        Args:
            backend_manager: BackendManager instance to monitor
        """
        self.backend_manager = backend_manager

        # Initialize circuit states
        for backend_name in backend_manager.backends:
            self.circuit_states[backend_name] = "CLOSED"
            self.error_counts[backend_name] = 0
            self.failure_timestamps[backend_name] = []

        # Start background checking task
        self.check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Health checker started")

    async def stop(self) -> None:
        """Stop background health checking."""
        if self.check_task:
            self.check_task.cancel()
            try:
                await self.check_task
            except asyncio.CancelledError:
                pass
            logger.info("Health checker stopped")

    async def _health_check_loop(self) -> None:
        """Background loop that checks backend health periodically."""
        while True:
            try:
                await asyncio.sleep(self.check_interval)

                for backend_name, backend in (
                    self.backend_manager.backends.items()
                ):
                    if not backend.config.health_check.enabled:
                        continue

                    await self._check_backend(backend)

                # Refresh capabilities if cache expired
                if self.backend_manager.is_capability_cache_expired():
                    await self.backend_manager.refresh_capabilities()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")

    async def _check_backend(self, backend: "Backend") -> None:  # noqa: F821
        """Perform health check on a single backend.

        Args:
            backend: Backend to check
        """
        backend_name = backend.config.name
        try:
            logger.debug(f"Health checking backend: {backend_name}")
            is_healthy = await backend.client.health_check()

            if is_healthy:
                self.record_success(backend_name)
                logger.debug(f"Backend {backend_name} is healthy")
            else:
                error = Exception("Health check returned False")
                self.record_failure(backend_name, error)
                logger.warning(f"Backend {backend_name} health check failed")

        except Exception as e:
            logger.warning(f"Health check failed for {backend_name}: {e}")
            self.record_failure(backend_name, e)

    def record_success(self, backend_name: str) -> None:
        """Record successful request to backend.

        Args:
            backend_name: Name of the backend
        """
        self.error_counts[backend_name] = 0
        self.failure_timestamps[backend_name] = []

        # Transition HALF_OPEN -> CLOSED on success
        if self.circuit_states.get(backend_name) == "HALF_OPEN":
            self.circuit_states[backend_name] = "CLOSED"
            logger.info(
                f"Circuit breaker for {backend_name} closed (recovered)"
            )

    def record_failure(self, backend_name: str, error: Exception) -> None:
        """Record failed request to backend.

        Args:
            backend_name: Name of the backend
            error: The exception that occurred
        """
        if backend_name not in self.error_counts:
            self.error_counts[backend_name] = 0
        if backend_name not in self.failure_timestamps:
            self.failure_timestamps[backend_name] = []

        self.error_counts[backend_name] += 1
        self.failure_timestamps[backend_name].append(datetime.now())
        self.last_check_times[backend_name] = datetime.now()

        logger.debug(
            f"Recorded failure for {backend_name} "
            f"(count: {self.error_counts[backend_name]}, error: {error})"
        )

        # Get circuit breaker config
        backend = self.backend_manager.backends.get(backend_name)
        if not backend:
            return

        cb_config = backend.config.circuit_breaker
        threshold = cb_config.failure_threshold

        # Update backend health status
        backend.health_status.error_count = self.error_counts[backend_name]
        backend.health_status.last_error = str(error)
        backend.health_status.circuit_state = self.circuit_states.get(
            backend_name, "CLOSED"
        )

        # Open circuit if threshold exceeded
        if (
            self.error_counts[backend_name] >= threshold
            and self.circuit_states.get(backend_name) != "OPEN"
        ):
            self.circuit_states[backend_name] = "OPEN"
            self.circuit_timeouts[backend_name] = datetime.now() + timedelta(
                seconds=cb_config.timeout_seconds
            )
            logger.warning(
                f"Circuit breaker for {backend_name} opened "
                f"(failures: {self.error_counts[backend_name]})"
            )

    def is_circuit_open(self, backend_name: str) -> bool:
        """Check if circuit breaker is open for a backend.

        Args:
            backend_name: Name of the backend

        Returns:
            True if circuit is OPEN or HALF_OPEN, False if CLOSED
        """
        state = self.circuit_states.get(backend_name, "CLOSED")

        if state == "CLOSED":
            return False
        elif state == "OPEN":
            # Check if timeout has elapsed
            timeout = self.circuit_timeouts.get(backend_name)
            if timeout and datetime.now() >= timeout:
                # Attempt recovery
                self.circuit_states[backend_name] = "HALF_OPEN"
                logger.info(
                    f"Circuit breaker for {backend_name} "
                    f"transitioned to HALF_OPEN"
                )
                return True

            return True
        else:  # HALF_OPEN
            return True

    async def attempt_circuit_recovery(self, backend_name: str) -> bool:
        """Attempt to recover a circuit by testing the backend.

        Args:
            backend_name: Name of the backend to test

        Returns:
            True if recovery was successful, False otherwise
        """
        backend = self.backend_manager.backends.get(backend_name)
        if not backend:
            return False

        logger.debug(f"Attempting circuit recovery for {backend_name}")

        try:
            is_healthy = await backend.client.health_check()
            if is_healthy:
                self.record_success(backend_name)
                return True
            else:
                error = Exception("Recovery health check failed")
                self.record_failure(backend_name, error)
                return False
        except Exception as e:
            logger.debug(f"Recovery check failed for {backend_name}: {e}")
            self.record_failure(backend_name, e)
            return False

    def get_health_status(self, backend_name: str) -> HealthStatus:
        """Get health status for a backend.

        Args:
            backend_name: Name of the backend

        Returns:
            HealthStatus object
        """
        backend = self.backend_manager.backends.get(backend_name)
        if not backend:
            return HealthStatus(backend_name=backend_name)

        backend.health_status.error_count = self.error_counts.get(
            backend_name, 0
        )
        backend.health_status.circuit_state = self.circuit_states.get(
            backend_name, "CLOSED"
        )
        backend.health_status.last_check = self.last_check_times.get(
            backend_name, datetime.now()
        )
        backend.health_status.is_healthy = not self.is_circuit_open(
            backend_name
        )

        return backend.health_status
