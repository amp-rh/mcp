# /commit

Stage and commit changes with a conventional commit message.

## Usage

```
/commit
```

## Steps

1. Run `git status` to see changed files
2. Review changes with `git diff`
3. Stage appropriate files with `git add`
4. Create commit message following conventional commits:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation only
   - `refactor:` - Code refactoring
   - `test:` - Adding/updating tests
   - `chore:` - Maintenance tasks
5. Commit with `git commit -m "type: description"`

## Example

```bash
git add src/mcp_server/tools/new_tool.py tests/test_new_tool.py
git commit -m "feat: add new_tool for data processing"
```

