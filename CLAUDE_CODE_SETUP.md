# Claude Code Installation Guide

This guide covers installing and using this MCP server with Claude Code.

## Quick Installation

### Option 1: Direct from GitHub (Easiest - No Clone Required)

**Template Mode (Recommended for Getting Started):**
```bash
claude mcp add --transport stdio mcp-server \
  -- uv run --with "git+https://github.com/amp-rh/mcp.git" mcp-server
```

**Router Mode (Requires Backend Configuration):**
```bash
# First, create a backends.yaml file somewhere accessible
# Then install with the config path
claude mcp add --transport stdio mcp-router \
  --env MCP_BACKENDS_CONFIG=/path/to/backends.yaml \
  -- uv run --with "git+https://github.com/amp-rh/mcp.git" mcp-router
```

**Verify:**
```bash
claude mcp list
```

**Advantages:**
- No need to clone the repository
- Always uses latest version from GitHub
- One command installation
- Perfect for end users
- Auto-updates when you reinstall

### Option 2: Automated Script (For Local Development)

```bash
./install-to-claude.sh
```

The script will:
- Check prerequisites (Claude Code, uv)
- Install dependencies
- Prompt you to choose template or router mode
- Configure Claude Code automatically
- Verify installation

### Option 2: Using Makefile

```bash
make install-claude
```

### Option 3: Project-Scoped Configuration

This project includes a `.mcp.json` file. When you open Claude Code in this directory, it will:
1. Detect the `.mcp.json` configuration
2. Prompt you to approve the MCP servers
3. Automatically configure them for this project

**Advantage**: Team members can use the same configuration (commit `.mcp.json` to git)

### Option 4: Manual Local Installation

```bash
# Clone the repository
git clone https://github.com/amp-rh/mcp.git
cd mcp

# Install dependencies
uv sync

# Add to Claude Code
claude mcp add --transport stdio mcp-server \
  --env MCP_SERVER_NAME=mcp-server \
  -- uv --directory "$(pwd)" run mcp-server

# Verify
claude mcp list
```

## Installation Methods Comparison

| Method | Best For | Pros | Cons |
|--------|----------|------|------|
| Direct from GitHub | End users | No clone needed, one command | Can't customize easily |
| Automated script | Local dev | Easy setup, mode selection | Requires clone |
| Project-scoped | Teams | Shared config, version control | Requires clone |
| Manual | Advanced users | Full control | More steps |

## Choosing Between Template and Router Mode

### Template Mode (mcp-server)
**Use when:**
- You want a simple, standalone MCP server
- You're just getting started
- You don't need to aggregate multiple backends

**Provides:**
- 3 example tools (greet, calculate_sum, reverse_string)
- Ready to customize with your own tools
- No additional configuration needed

### Router Mode (mcp-router)
**Use when:**
- You have multiple MCP backend servers
- You need advanced routing strategies
- You want health checking and circuit breakers

**Requires:**
- At least one backend MCP server running
- Configuration in `config/backends.yaml`

## Verifying Installation

```bash
# Check server status
claude mcp list

# In Claude Code session
/mcp

# Test a tool (template mode)
# Just ask: "Can you greet me?"
```

## Uninstalling

```bash
# Automated
./uninstall-from-claude.sh

# Or using make
make uninstall-claude

# Or manually
claude mcp remove mcp-server
claude mcp remove mcp-router
```

## Customizing

### Adding Your Own Tools

1. Edit `src/mcp_server/tools/example_tools.py`
2. Add new tool functions with `@mcp.tool` decorator
3. Restart Claude Code or run `/mcp` to reload

Example:
```python
@mcp.tool
def fetch_weather(city: str) -> dict:
    """Get weather for a city."""
    # Your implementation
    return {"city": city, "temp": 72}
```

### Adding Resources

1. Create file in `src/mcp_server/resources/`
2. Use `@mcp.resource` decorator
3. Register in `resources/__init__.py`

### Adding Prompts

1. Create file in `src/mcp_server/prompts/`
2. Use `@mcp.prompt` decorator
3. Register in `prompts/__init__.py`

## Troubleshooting

### "No MCP servers configured"
- You're in a different directory than the project
- Run `claude mcp list` to check configuration
- Re-run installation script

### "Failed to connect"
- For router mode: check that backends are configured in `config/backends.yaml`
- For router mode: ensure backend servers are running
- Try template mode instead: `./install-to-claude.sh` and choose option 1

### Server not appearing after installation
- Check that `uv` is installed: `which uv`
- Verify dependencies: `uv sync`
- Check Claude Code logs for errors

### Tools not updating
- Changes to tools require restarting the MCP server
- In Claude Code, you may need to restart the session
- Or run `/mcp` to reload

## Project-Scoped vs Local vs User Scope

**Project scope** (`.mcp.json`):
- Shared with team (commit to git)
- Only active in this project directory
- Requires approval on first use

**Local scope** (`~/.claude.json` for this project):
- Personal configuration
- Only for this project
- Doesn't affect team members

**User scope** (`~/.claude.json` globally):
- Available in all projects
- Personal to you
- Use `--scope user` flag

## Environment Variables

You can customize the server using environment variables in the MCP configuration:

```json
{
  "mcpServers": {
    "mcp-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/path/to/mcp", "run", "mcp-server"],
      "env": {
        "MCP_SERVER_NAME": "my-custom-name",
        "MCP_PORT": "8000"
      }
    }
  }
}
```

See `src/mcp_server/config.py` for all available environment variables.

## Next Steps

- Read `CLAUDE.md` for development guidelines
- Check `README.md` for architecture details
- See `/.agents/docs/` for detailed patterns and conventions
- Explore example tools in `src/mcp_server/tools/example_tools.py`

## Support

- GitHub Issues: https://github.com/amp-rh/mcp/issues
- Documentation: See README.md and CLAUDE.md
- Claude Code Docs: https://code.claude.com/docs/en/mcp
