"""Tests for health checking and circuit breaker."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock

from mcp_server.routing.health import HealthChecker


class TestHealthChecker:
    """Test HealthChecker functionality."""

    def test_health_checker_initialization(self):
        """Test HealthChecker initialization."""
        checker = HealthChecker(check_interval=30)
        assert checker.check_interval == 30
        assert checker.circuit_states == {}
        assert checker.error_counts == {}

    def test_record_failure_increments_count(self):
        """Test that recording failure increments error count."""
        checker = HealthChecker()
        # Initialize state
        checker.error_counts["test-backend"] = 0
        checker.circuit_states["test-backend"] = "CLOSED"
        checker.failure_timestamps["test-backend"] = []
        checker.backend_manager = MagicMock()
        checker.backend_manager.backends = {
            "test-backend": MagicMock(
                config=MagicMock(
                    circuit_breaker=MagicMock(
                        failure_threshold=5,
                        timeout_seconds=60,
                    )
                ),
                health_status=MagicMock(),
            )
        }

        error = Exception("Connection refused")
        checker.record_failure("test-backend", error)

        assert checker.error_counts["test-backend"] == 1

    def test_circuit_opens_on_threshold(self):
        """Test that circuit opens when failure threshold is exceeded."""
        checker = HealthChecker()
        # Initialize state
        checker.error_counts["test-backend"] = 0
        checker.circuit_states["test-backend"] = "CLOSED"
        checker.failure_timestamps["test-backend"] = []
        checker.backend_manager = MagicMock()
        checker.backend_manager.backends = {
            "test-backend": MagicMock(
                config=MagicMock(
                    circuit_breaker=MagicMock(
                        failure_threshold=3,
                        timeout_seconds=60,
                    )
                ),
                health_status=MagicMock(),
            )
        }

        # Record failures up to threshold
        for _ in range(3):
            checker.record_failure(
                "test-backend",
                Exception("Connection refused"),
            )

        assert checker.circuit_states["test-backend"] == "OPEN"

    def test_circuit_stays_closed_below_threshold(self):
        """Test that circuit stays closed below failure threshold."""
        checker = HealthChecker()
        # Initialize state
        checker.error_counts["test-backend"] = 0
        checker.circuit_states["test-backend"] = "CLOSED"
        checker.failure_timestamps["test-backend"] = []
        checker.backend_manager = MagicMock()
        checker.backend_manager.backends = {
            "test-backend": MagicMock(
                config=MagicMock(
                    circuit_breaker=MagicMock(
                        failure_threshold=5,
                        timeout_seconds=60,
                    )
                ),
                health_status=MagicMock(),
            )
        }

        # Record failures below threshold
        for _ in range(2):
            checker.record_failure(
                "test-backend",
                Exception("Connection refused"),
            )

        assert checker.circuit_states["test-backend"] == "CLOSED"

    def test_record_success_resets_count(self):
        """Test that recording success resets error count."""
        checker = HealthChecker()
        # Initialize state
        checker.error_counts["test-backend"] = 5
        checker.circuit_states["test-backend"] = "CLOSED"
        checker.failure_timestamps["test-backend"] = [datetime.now()]

        checker.record_success("test-backend")

        assert checker.error_counts["test-backend"] == 0
        assert checker.failure_timestamps["test-backend"] == []

    def test_circuit_closes_on_success_in_half_open(self):
        """Test that circuit closes when success occurs in HALF_OPEN state."""
        checker = HealthChecker()
        # Initialize state
        checker.error_counts["test-backend"] = 0
        checker.circuit_states["test-backend"] = "HALF_OPEN"
        checker.failure_timestamps["test-backend"] = []

        checker.record_success("test-backend")

        assert checker.circuit_states["test-backend"] == "CLOSED"

    def test_is_circuit_open_closed_state(self):
        """Test is_circuit_open returns False for CLOSED state."""
        checker = HealthChecker()
        checker.circuit_states["test-backend"] = "CLOSED"

        assert checker.is_circuit_open("test-backend") is False

    def test_is_circuit_open_open_state(self):
        """Test is_circuit_open returns True for OPEN state."""
        checker = HealthChecker()
        checker.circuit_states["test-backend"] = "OPEN"
        checker.circuit_timeouts["test-backend"] = datetime.now() + timedelta(
            seconds=60
        )

        assert checker.is_circuit_open("test-backend") is True

    def test_is_circuit_open_half_open_state(self):
        """Test is_circuit_open returns True for HALF_OPEN state."""
        checker = HealthChecker()
        checker.circuit_states["test-backend"] = "HALF_OPEN"

        assert checker.is_circuit_open("test-backend") is True

    def test_circuit_transitions_to_half_open_after_timeout(self):
        """Test circuit transitions to HALF_OPEN after timeout."""
        checker = HealthChecker()
        # Initialize state with expired timeout
        checker.circuit_states["test-backend"] = "OPEN"
        checker.circuit_timeouts["test-backend"] = datetime.now() - timedelta(seconds=1)

        # Call is_circuit_open which should trigger transition
        is_open = checker.is_circuit_open("test-backend")

        assert is_open is True
        assert checker.circuit_states["test-backend"] == "HALF_OPEN"

    def test_get_health_status(self):
        """Test getting health status for a backend."""
        from mcp_server.routing.models import HealthStatus

        checker = HealthChecker()
        # Initialize state
        checker.error_counts["test-backend"] = 2
        checker.circuit_states["test-backend"] = "CLOSED"
        checker.last_check_times["test-backend"] = datetime.now()
        checker.backend_manager = MagicMock()
        checker.backend_manager.backends = {
            "test-backend": MagicMock(
                health_status=HealthStatus(backend_name="test-backend")
            )
        }

        status = checker.get_health_status("test-backend")

        assert status.backend_name == "test-backend"
        assert status.error_count == 2
        assert status.circuit_state == "CLOSED"

    def test_error_count_persistence(self):
        """Test that error count persists across checks."""
        checker = HealthChecker()
        # Initialize state
        checker.error_counts["test-backend"] = 0
        checker.circuit_states["test-backend"] = "CLOSED"
        checker.failure_timestamps["test-backend"] = []
        checker.backend_manager = MagicMock()
        checker.backend_manager.backends = {
            "test-backend": MagicMock(
                config=MagicMock(
                    circuit_breaker=MagicMock(
                        failure_threshold=5,
                        timeout_seconds=60,
                    )
                ),
                health_status=MagicMock(),
            )
        }

        # Record first failure
        checker.record_failure(
            "test-backend",
            Exception("Error 1"),
        )
        assert checker.error_counts["test-backend"] == 1

        # Record second failure
        checker.record_failure(
            "test-backend",
            Exception("Error 2"),
        )
        assert checker.error_counts["test-backend"] == 2

    def test_last_error_stored(self):
        """Test that last error message is stored."""
        checker = HealthChecker()
        # Initialize state
        checker.error_counts["test-backend"] = 0
        checker.circuit_states["test-backend"] = "CLOSED"
        checker.failure_timestamps["test-backend"] = []
        checker.backend_manager = MagicMock()
        checker.backend_manager.backends = {
            "test-backend": MagicMock(
                config=MagicMock(
                    circuit_breaker=MagicMock(
                        failure_threshold=5,
                        timeout_seconds=60,
                    )
                ),
                health_status=MagicMock(),
            )
        }

        error = Exception("Database connection timeout")
        checker.record_failure("test-backend", error)

        status = checker.get_health_status("test-backend")
        assert "Database connection timeout" in status.last_error
