from dataclasses import dataclass


@dataclass(frozen=True)
class RoutingDecision:
    backend_name: str
    reason: str
    alternatives: tuple[str, ...] = ()
    strategy_used: str = ""

    def __post_init__(self) -> None:
        if not self.backend_name:
            raise ValueError("Backend name cannot be empty")
        if not self.reason:
            raise ValueError("Routing reason cannot be empty")
