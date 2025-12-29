# MCP Server Template - UBI9 Rootless Container
# Build: podman build -t mcp-template:latest .
# Run: podman run --rm -p 8000:8000 mcp-template:latest

FROM registry.access.redhat.com/ubi9/python-311:latest

LABEL name="mcp-template" \
      version="0.1.0" \
      description="FastMCP server template with tools, resources, and prompts"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

# Set working directory
WORKDIR /opt/app-root/src

# Copy dependency files first for better caching
COPY pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir .

# Copy source code
COPY src/ ./src/

# Install the package
RUN pip install --no-cache-dir -e .

# Expose the server port
EXPOSE 8000

# Run as non-root user (already configured in UBI9 Python image)
USER 1001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the MCP server with SSE transport
CMD ["python", "-m", "fastmcp", "run", "src/mcp_server/server.py:mcp", "--transport", "sse", "--port", "8000", "--host", "0.0.0.0"]

