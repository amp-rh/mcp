from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProcessConfig:
    command: str
    args: tuple[str, ...] = ()
    port: int | None = None
    env: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.command:
            raise ValueError("Process command cannot be empty")
        if self.port is not None and (self.port < 1 or self.port > 65535):
            raise ValueError(f"Invalid port number: {self.port}")
