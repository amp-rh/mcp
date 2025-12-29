# Pull Request Workflow

See @AGENTS.md for project-wide rules.

## Before Creating PR

1. Ensure all tests pass: `make test`
2. Run linting: `make lint`
3. Format code: `make format`

## PR Checklist

- [ ] Tests added for new functionality
- [ ] All tests passing
- [ ] Linting passes
- [ ] Documentation updated if needed
- [ ] AGENTS.md files updated if structure changed

## Commit Messages

Use conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code refactoring
- `test:` - Adding/updating tests
- `chore:` - Maintenance tasks

## Examples

```bash
git commit -m "feat: add weather lookup tool"
git commit -m "fix: handle empty input in greet tool"
git commit -m "docs: update README with deployment instructions"
```

## Related

- @.agents/commands/commit.md - Commit command
- @.agents/docs/workflows/testing.md - Testing workflow

