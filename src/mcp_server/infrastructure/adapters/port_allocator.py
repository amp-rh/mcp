import socket

from mcp_server.application.ports import PortAllocatorPort
from mcp_server.domain.exceptions import ProcessManagementError


class PortAllocator(PortAllocatorPort):
    def __init__(self, start_port: int = 8100, end_port: int = 8200) -> None:
        self.start_port = start_port
        self.end_port = end_port
        self._allocated: set[int] = set()

    async def allocate_port(self) -> int:
        for port in range(self.start_port, self.end_port):
            if port in self._allocated:
                continue

            if self._is_port_available(port):
                self._allocated.add(port)
                return port

        raise ProcessManagementError("No available ports in range")

    async def release_port(self, port: int) -> None:
        self._allocated.discard(port)

    def _is_port_available(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return True
            except OSError:
                return False
