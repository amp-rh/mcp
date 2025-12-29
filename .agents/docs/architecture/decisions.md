# Architecture Decision Records

See @AGENTS.md for project-wide rules.

## Overview

This document records significant architectural decisions for this project.

---

## ADR-001: Use FastMCP for MCP Server Implementation

**Status**: Accepted

**Context**: Need to implement an MCP server that exposes tools, resources, and prompts.

**Decision**: Use FastMCP library as the MCP server framework.

**Rationale**:
- Pythonic decorator-based API
- Built-in support for multiple transports (stdio, HTTP/SSE)
- Active development and good documentation
- Handles protocol complexity internally

**Consequences**:
- Dependent on FastMCP library updates
- Must follow FastMCP patterns for tools/resources/prompts

---

## ADR-002: Modular Component Organization

**Status**: Accepted

**Context**: Need to organize tools, resources, and prompts in a maintainable way.

**Decision**: Separate modules for each component type with registration functions.

**Rationale**:
- Clear separation of concerns
- Easy to add new components
- Follows single responsibility principle
- Enables independent testing

**Consequences**:
- Slightly more boilerplate for registration
- Need to maintain AGENTS.md in each module

---

## ADR-003: HTTP/SSE as Primary Transport

**Status**: Accepted

**Context**: Need to choose a default transport mechanism.

**Decision**: Use HTTP/SSE as the primary transport for web deployments.

**Rationale**:
- Works with web-based AI clients
- Easy to containerize and deploy
- Standard HTTP ports and protocols
- SSE provides efficient server-push

**Consequences**:
- Requires network configuration for container deployment
- May need stdio transport for CLI integrations

---

## ADR-004: UBI9 Rootless Container

**Status**: Accepted

**Context**: Need a container base image for deployment.

**Decision**: Use UBI9 Python image with rootless configuration.

**Rationale**:
- Enterprise-ready base image
- Security-focused (rootless)
- Compatible with OpenShift and Kubernetes
- Matches python-project-template conventions

**Consequences**:
- Larger base image than Alpine
- Requires Red Hat registry access (or use public UBI)

---

## Template for New Decisions

```markdown
## ADR-XXX: Title

**Status**: Proposed | Accepted | Deprecated | Superseded

**Context**: What is the issue?

**Decision**: What did we decide?

**Rationale**: Why did we decide this?

**Consequences**: What are the trade-offs?
```

