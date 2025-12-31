from dataclasses import dataclass


@dataclass(frozen=True)
class BackendRegistrationRequest:
    source: str
    name: str | None = None
    namespace: str | None = None
    priority: int = 10
    auto_start: bool = True
    health_check_enabled: bool = True


@dataclass(frozen=True)
class BackendRegistrationResponse:
    backend_name: str
    namespace: str
    url: str
    started: bool
    message: str
