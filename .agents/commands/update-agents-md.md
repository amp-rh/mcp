# /update-agents-md

Update AGENTS.md files to reflect current project state.

## Usage

```
/update-agents-md
```

## Steps

1. List all AGENTS.md files in project
2. For each file, verify:
   - Structure matches actual directory contents
   - Links to documentation are valid
   - Rules are current and accurate
3. Update any outdated sections
4. Add new entries for new files/directories

## Locations to Check

- `AGENTS.md` - Root index
- `.agents/AGENTS.md` - Agent resources
- `.agents/commands/AGENTS.md` - Commands
- `.agents/scratch/AGENTS.md` - Scratch workspace
- `src/AGENTS.md` - Source code
- `src/mcp_server/tools/AGENTS.md` - Tools
- `src/mcp_server/resources/AGENTS.md` - Resources
- `src/mcp_server/prompts/AGENTS.md` - Prompts
- `tests/AGENTS.md` - Tests

