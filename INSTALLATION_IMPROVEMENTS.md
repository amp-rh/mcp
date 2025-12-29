# Installation Improvements for Claude Code

This document summarizes the streamlining improvements made to make installing this MCP server easier for Claude Code users.

## Summary of Improvements

### 1. Direct GitHub Installation ✨ (NEW - Easiest)

**Before:** Users had to clone repo, install deps, configure manually
**After:** One-line installation from GitHub

```bash
claude mcp add --transport stdio mcp-server \
  -- uv run --with "git+https://github.com/amp-rh/mcp.git" mcp-server
```

**Benefits:**
- Zero setup - no cloning required
- Always uses latest version
- Perfect for end users who just want to use the tools
- Works from any directory

### 2. Automated Installation Script

Created `install-to-claude.sh` that:
- ✅ Checks prerequisites (Claude Code CLI, uv)
- ✅ Installs dependencies automatically
- ✅ Prompts for mode selection (template vs router)
- ✅ Handles existing installations
- ✅ Provides clear next steps

Usage:
```bash
./install-to-claude.sh
```

### 3. Project-Scoped Configuration

Created `.mcp.json` in project root:
- ✅ Pre-configured for both template and router modes
- ✅ Team members can share configuration (commit to git)
- ✅ Supports `${PROJECT_DIR}` variable for portability
- ✅ Router mode pre-configured but disabled by default

**User Experience:**
1. Clone repo and `cd` into it
2. Open Claude Code
3. Approve MCP server when prompted
4. Done!

### 4. Makefile Targets

Added convenient make targets:
```bash
make install-claude    # Install to Claude Code
make uninstall-claude  # Remove from Claude Code
```

### 5. Uninstall Script

Created `uninstall-from-claude.sh`:
- Cleanly removes both template and router modes
- Provides feedback on what was removed
- Simple one-command uninstall

### 6. Improved Error Messages

**Before:**
```
ConfigurationError: At least one backend must be configured
```

**After:**
```
ConfigurationError: At least one backend must be configured.
Please edit config/backends.yaml and add backend servers.
See config/backends.yaml.example for examples.
For a simple MCP server without routing, use 'mcp-server' instead of 'mcp-router'.
```

### 7. Comprehensive Documentation

Created dedicated documentation:
- **CLAUDE_CODE_SETUP.md** - Complete installation guide
- Updated **README.md** - Quick start at the top
- **This file** - Summary of improvements

### 8. Installation Options Matrix

Users now have clear choices:

| Method | Command | Best For |
|--------|---------|----------|
| Direct from GitHub | `claude mcp add --transport stdio mcp-server -- uv run --with "git+https://github.com/amp-rh/mcp.git" mcp-server` | End users, quick testing |
| Automated script | `./install-to-claude.sh` | Local development, choosing modes |
| Project-scoped | Open in Claude Code, approve `.mcp.json` | Teams, shared config |
| Makefile | `make install-claude` | Developers familiar with make |
| Manual | See CLAUDE_CODE_SETUP.md | Advanced users, custom setups |

## Installation Flow Comparison

### Before Improvements:
1. Clone repository
2. Install uv if not present
3. Run `uv sync`
4. Find the right `claude mcp add` command
5. Copy/paste and modify paths
6. Debug path issues
7. Debug configuration issues
8. Maybe give up and ask for help

**Time:** 10-15 minutes (if you know what you're doing)

### After Improvements (Direct from GitHub):
1. Copy one command from README
2. Paste and run

**Time:** 30 seconds

### After Improvements (Local Development):
1. Clone repository
2. Run `./install-to-claude.sh`
3. Choose template or router mode
4. Done

**Time:** 2 minutes

## Key Benefits

### For End Users:
- ✅ No need to understand the project structure
- ✅ No need to clone repositories
- ✅ No need to manage dependencies
- ✅ One command to install
- ✅ One command to uninstall
- ✅ Clear error messages

### For Developers:
- ✅ Scripts for automation
- ✅ Makefile integration
- ✅ Local development friendly
- ✅ Easy to customize
- ✅ Project-scoped configuration

### For Teams:
- ✅ Shared `.mcp.json` configuration
- ✅ Version controlled setup
- ✅ Consistent across team members
- ✅ Easy onboarding

## Files Created/Modified

### New Files:
- `.mcp.json` - Project-scoped MCP configuration
- `install-to-claude.sh` - Automated installation script
- `uninstall-from-claude.sh` - Automated uninstall script
- `CLAUDE_CODE_SETUP.md` - Detailed installation guide
- `INSTALLATION_IMPROVEMENTS.md` - This file

### Modified Files:
- `README.md` - Added Claude Code quick start section
- `Makefile` - Added install-claude and uninstall-claude targets
- `src/mcp_server/routing/config_loader.py` - Improved error messages
- `config/backends.yaml` - Commented out example backend

## Testing the Installation

### Test Direct GitHub Installation:
```bash
# Install
claude mcp add --transport stdio mcp-server-test \
  -- uv run --with "git+https://github.com/amp-rh/mcp.git" mcp-server

# Verify
claude mcp list

# Test in Claude Code
# Open Claude Code and type: /mcp
# Ask: "Can you greet me?"

# Uninstall
claude mcp remove mcp-server-test
```

### Test Local Installation:
```bash
# Clone and install
git clone https://github.com/amp-rh/mcp.git
cd mcp
./install-to-claude.sh

# Verify
claude mcp list

# Uninstall
./uninstall-from-claude.sh
```

## Future Improvements

Potential enhancements:
1. **Auto-detection**: Detect Claude Code and offer to install automatically
2. **Version pinning**: Support installing specific versions/tags
3. **Update command**: Script to update to latest version
4. **Health check**: Command to verify installation and test tools
5. **Configuration wizard**: Interactive config builder for router mode
6. **GitHub Actions**: CI/CD to test installation on different platforms

## Conclusion

These improvements reduce the barrier to entry from ~15 minutes of technical setup to 30 seconds for end users. The installation process is now:
- **Simpler**: One command instead of many
- **Faster**: Seconds instead of minutes
- **More Reliable**: Automated checks and clear errors
- **More Flexible**: Multiple installation methods for different use cases
- **Better Documented**: Clear guides and examples

The direct GitHub installation method is particularly powerful as it requires zero local setup and always provides the latest version.
