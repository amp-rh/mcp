import fnmatch

from mcp_server.domain.entities import Backend
from mcp_server.domain.exceptions import RoutingError
from mcp_server.domain.value_objects import RoutingDecision


def route_by_capability(tool_name: str, backends: list[Backend]) -> RoutingDecision:
    if not backends:
        raise RoutingError("No backends available", tool_name=tool_name)

    healthy_backends = [b for b in backends if b.is_healthy]
    if not healthy_backends:
        raise RoutingError("No healthy backends available", tool_name=tool_name)

    candidates = [b for b in healthy_backends if b.has_tool(tool_name)]
    if not candidates:
        raise RoutingError(
            f"No backend has capability for tool: {tool_name}",
            tool_name=tool_name,
        )

    sorted_candidates = sorted(candidates, key=lambda b: b.config.priority)
    selected = sorted_candidates[0]

    return RoutingDecision(
        backend_name=selected.name,
        reason="Backend has the required tool capability",
        alternatives=tuple(b.name for b in sorted_candidates[1:]),
        strategy_used="capability",
    )


def route_by_path(tool_name: str, backends: list[Backend]) -> RoutingDecision:
    if not backends:
        raise RoutingError("No backends available", tool_name=tool_name)

    healthy_backends = [b for b in backends if b.is_healthy]
    if not healthy_backends:
        raise RoutingError("No healthy backends available", tool_name=tool_name)

    candidates_with_pattern = []
    for backend in healthy_backends:
        for route in backend.config.routes:
            if fnmatch.fnmatch(tool_name, route.pattern):
                candidates_with_pattern.append((backend, route.pattern))
                break

    if not candidates_with_pattern:
        raise RoutingError(
            f"No path-based route found for tool: {tool_name}",
            tool_name=tool_name,
        )

    sorted_candidates = sorted(
        candidates_with_pattern,
        key=lambda x: x[0].config.priority,
    )
    selected_backend, matched_pattern = sorted_candidates[0]

    return RoutingDecision(
        backend_name=selected_backend.name,
        reason=f"Matched path pattern '{matched_pattern}'",
        alternatives=tuple(b.name for b, _ in sorted_candidates[1:]),
        strategy_used="path",
    )


def route_by_fallback(tool_name: str, backends: list[Backend]) -> RoutingDecision:
    if not backends:
        raise RoutingError("No backends available", tool_name=tool_name)

    healthy_backends = [b for b in backends if b.is_healthy]
    if not healthy_backends:
        raise RoutingError("No healthy backends available", tool_name=tool_name)

    sorted_backends = sorted(healthy_backends, key=lambda b: b.config.priority)
    selected = sorted_backends[0]

    return RoutingDecision(
        backend_name=selected.name,
        reason=f"Using fallback chain (priority: {selected.config.priority})",
        alternatives=tuple(b.name for b in sorted_backends[1:]),
        strategy_used="fallback",
    )
