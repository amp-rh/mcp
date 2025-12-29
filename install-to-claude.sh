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

# Install dependencies
echo "📦 Installing dependencies..."
uv sync
echo

# Prompt user for mode selection
echo "Which mode would you like to install?"
echo "1) Template Server (standalone, recommended for getting started)"
echo "2) Router Server (aggregates multiple MCP backends)"
read -p "Enter choice [1-2]: " mode_choice

case $mode_choice in
    1)
        SERVER_NAME="mcp-server"
        COMMAND="mcp-server"
        echo "Installing template server mode..."
        ;;
    2)
        SERVER_NAME="mcp-router"
        COMMAND="mcp-router"
        echo "Installing router server mode..."
        echo "⚠️  Note: Router mode requires backend servers configured in config/backends.yaml"
        ;;
    *)
        echo "Invalid choice. Defaulting to template server mode."
        SERVER_NAME="mcp-server"
        COMMAND="mcp-server"
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
