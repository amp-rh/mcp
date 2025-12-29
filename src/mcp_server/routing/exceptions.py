"""Routing-specific exceptions."""


class RouterError(Exception):
    """Base exception for all routing-related errors."""

    def __init__(
        self,
        message: str,
        backend: str | None = None,
        original_error: Exception | None = None,
        routing_decision: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.backend = backend
        self.original_error = original_error
        self.routing_decision = routing_decision

    def to_dict(self) -> dict:
        """Convert exception to dictionary for error responses."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "backend": self.backend,
            "routing_decision": self.routing_decision,
            "original_error": str(self.original_error)
            if self.original_error
            else None,
        }


class BackendUnavailableError(RouterError):
    """Raised when a backend is unavailable (circuit open or unreachable)."""

    pass


class RoutingError(RouterError):
    """Raised when no suitable routing path is found."""

    pass


class BackendTimeoutError(RouterError):
    """Raised when a backend request times out."""

    pass


class ConfigurationError(RouterError):
    """Raised when router configuration is invalid."""

    pass


class CapabilityDiscoveryError(RouterError):
    """Raised when capability discovery from backend fails."""

    pass
