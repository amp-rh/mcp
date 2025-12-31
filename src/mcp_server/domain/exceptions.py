class DomainException(Exception):
    pass


class BackendNotFoundError(DomainException):
    def __init__(self, backend_name: str) -> None:
        super().__init__(f"Backend not found: {backend_name}")
        self.backend_name = backend_name


class NoHealthyBackendsError(DomainException):
    def __init__(self, message: str = "No healthy backends available") -> None:
        super().__init__(message)


class RoutingError(DomainException):
    def __init__(self, message: str, tool_name: str | None = None) -> None:
        super().__init__(message)
        self.tool_name = tool_name


class CircuitBreakerOpenError(DomainException):
    def __init__(self, backend_name: str) -> None:
        super().__init__(f"Circuit breaker is open for backend: {backend_name}")
        self.backend_name = backend_name


class InvalidConfigurationError(DomainException):
    pass


class ProcessManagementError(DomainException):
    pass


class BackendAlreadyExistsError(DomainException):
    def __init__(self, backend_name: str) -> None:
        super().__init__(f"Backend already exists: {backend_name}")
        self.backend_name = backend_name


class ConfigurationWatchError(DomainException):
    pass
