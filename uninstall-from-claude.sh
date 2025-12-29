#!/bin/bash
# Uninstallation script for removing this MCP server from Claude Code

echo "🗑️  Uninstalling MCP Server from Claude Code..."
echo

# Remove both possible server installations
for server in "mcp-server" "mcp-router"; do
    if claude mcp get "$server" &> /dev/null; then
        echo "Removing $server..."
        claude mcp remove "$server"
    fi
done

echo
echo "✅ Uninstallation complete!"
echo
echo "To reinstall, run: ./install-to-claude.sh"
