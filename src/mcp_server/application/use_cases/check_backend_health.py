from mcp_server.domain.repositories import BackendRepository
from mcp_server.domain.services import (
    should_attempt_half_open,
    should_close_circuit,
)


class CheckBackendHealth:
    def __init__(self, backend_repository: BackendRepository) -> None:
        self.backend_repository = backend_repository

    async def execute(self) -> None:
        backends = self.backend_repository.get_all()

        for backend in backends:
            if should_attempt_half_open(
                backend.health_status,
                backend.config.circuit_breaker,
            ):
                backend.half_open_circuit()

            if backend.health_status.error_count == 0:
                if should_close_circuit(
                    success_count=1,
                    settings=backend.config.circuit_breaker,
                ):
                    backend.close_circuit()
