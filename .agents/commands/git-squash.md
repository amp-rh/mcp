# /git-squash

Squash multiple commits into one.

## Usage

```
/git-squash [number_of_commits]
```

## Steps

1. Check commit history with `git log --oneline -n 10`
2. Run `git rebase -i HEAD~N` where N is number of commits
3. Mark commits to squash with `s` or `squash`
4. Edit the combined commit message
5. Force push if needed: `git push --force-with-lease`

## Example

```bash
# Squash last 3 commits
git rebase -i HEAD~3

# In editor, change 'pick' to 'squash' for commits to combine
# Save and edit final message
```

