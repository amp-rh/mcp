#!/bin/bash
# Installation script for adding this MCP server to Claude Code

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Installing MCP Server to Claude Code..."
echo

# Check if Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo "❌ Error: Claude Code CLI not found"
    echo "   Please install Claude Code first: https://claude.com/download"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv not found"
    echo "   Please install uv first: https://docs.astral.sh/uv/"
    exit 1
fi

# Parse command-line arguments
MODE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode=*)
            MODE="${1#*=}"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo
            echo "Options:"
            echo "  --mode=template    Install template server (non-interactive)"
            echo "  --mode=router      Install router server (non-interactive)"
            echo "  --help, -h         Show this help message"
            echo
            echo "If no options are provided, the script runs in interactive mode."
            exit 0
            ;;
        *)
            echo "❌ Error: Unknown option: $1"
            echo "   Run '$0 --help' for usage information"
            exit 1
            ;;
    esac
done

# Install dependencies
echo "📦 Installing dependencies..."
uv sync
echo

# Determine mode (interactive or non-interactive)
if [ -z "$MODE" ]; then
    # Interactive mode
    echo "Which mode would you like to install?"
    echo "1) Template Server (standalone, recommended for getting started)"
    echo "2) Router Server (aggregates multiple MCP backends)"
    read -p "Enter choice [1-2]: " mode_choice

    case $mode_choice in
        1)
            MODE="template"
            ;;
        2)
            MODE="router"
            ;;
        *)
            echo "Invalid choice. Defaulting to template server mode."
            MODE="template"
            ;;
    esac
else
    # Non-interactive mode - validate MODE value
    case $MODE in
        template|router)
            echo "Installing in non-interactive mode: $MODE"
            ;;
        *)
            echo "❌ Error: Invalid mode: $MODE"
            echo "   Valid modes: template, router"
            exit 1
            ;;
    esac
fi

# Validate backends.yaml for router mode
if [ "$MODE" = "router" ]; then
    BACKENDS_FILE="$SCRIPT_DIR/config/backends.yaml"

    if [ ! -f "$BACKENDS_FILE" ]; then
        echo "❌ Error: backends.yaml not found at $BACKENDS_FILE"
        echo "   Router mode requires a backends configuration file."
        echo "   Please create config/backends.yaml or use template mode instead."
        exit 1
    fi

    # Check if yq is available for validation
    if command -v yq &> /dev/null; then
        backend_count=$(yq '.backends | length' "$BACKENDS_FILE" 2>/dev/null || echo "0")
        if [ "$backend_count" -eq 0 ]; then
            echo "❌ Error: No backends configured in config/backends.yaml"
            echo "   Router mode requires at least one backend server."
            echo
            echo "   To fix this:"
            echo "   1. Edit config/backends.yaml and add backend servers, or"
            echo "   2. Use template mode instead: $0 --mode=template"
            exit 1
        fi
        echo "✓ Found $backend_count backend(s) configured"
    else
        echo "⚠️  Warning: yq not found - skipping backend validation"
        echo "   Install yq for automatic validation: https://github.com/mikefarah/yq"
    fi
fi

# Set server configuration based on mode
case $MODE in
    template)
        SERVER_NAME="mcp-server"
        COMMAND="mcp-server"
        echo "Installing template server mode..."
        ;;
    router)
        SERVER_NAME="mcp-router"
        COMMAND="mcp-router"
        echo "Installing router server mode..."
        ;;
esac

# Remove if already exists
if claude mcp get "$SERVER_NAME" &> /dev/null; then
    echo "Removing existing $SERVER_NAME..."
    claude mcp remove "$SERVER_NAME"
fi

# Add the server
echo "Adding $SERVER_NAME to Claude Code..."
if [ "$SERVER_NAME" = "mcp-router" ]; then
    claude mcp add --transport stdio "$SERVER_NAME" \
        --env "MCP_BACKENDS_CONFIG=$SCRIPT_DIR/config/backends.yaml" \
        -- uv --directory "$SCRIPT_DIR" run "$COMMAND"
else
    claude mcp add --transport stdio "$SERVER_NAME" \
        --env "MCP_SERVER_NAME=$SERVER_NAME" \
        -- uv --directory "$SCRIPT_DIR" run "$COMMAND"
fi

echo
echo "✅ Installation complete!"
echo
echo "Next steps:"
echo "  1. Run 'claude mcp list' to verify installation"
echo "  2. In Claude Code, type '/mcp' to see available tools"
echo "  3. Start using the tools in your conversation"
echo
echo "To customize:"
echo "  - Edit tools in: $SCRIPT_DIR/src/mcp_server/tools/"
echo "  - Edit resources in: $SCRIPT_DIR/src/mcp_server/resources/"
echo "  - Edit prompts in: $SCRIPT_DIR/src/mcp_server/prompts/"
