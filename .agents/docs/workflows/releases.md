# Release Process

See @AGENTS.md for project-wide rules.

## Version Numbering

Follow semantic versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

## Release Steps

1. Update version in `pyproject.toml` and `src/mcp_server/__init__.py`
2. Update CHANGELOG.md (if present)
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. Build and push container image

## Container Release

```bash
# Build with version tag
podman build -t mcp-template:v0.1.0 .
podman tag mcp-template:v0.1.0 mcp-template:latest

# Push to registry
podman push registry.example.com/mcp-template:v0.1.0
podman push registry.example.com/mcp-template:latest
```

## Version Files

Update version in:
- `pyproject.toml`: `version = "0.1.0"`
- `src/mcp_server/__init__.py`: `__version__ = "0.1.0"`

