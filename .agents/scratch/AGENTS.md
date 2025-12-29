# AGENTS.md - Scratch Workspace

See @AGENTS.md for project-wide rules.

## Overview

This directory is for working notes, decisions, and drafts during development sessions. Most files here are gitignored except templates.

## Structure

```
scratch/
├── AGENTS.md               # This file
├── session.md              # Current session context (gitignored)
├── decisions/              # Decision records
│   └── _template.md        # Decision template
├── notes/                  # Working notes
│   └── _template.md        # Notes template
├── context/                # Context files
│   └── _template.md        # Context template
├── research/               # Research notes
│   └── _template.md        # Research template
└── drafts/                 # Draft files (gitignored)
    └── .gitkeep
```

## Usage

1. Copy the relevant `_template.md` to create a new file
2. Name files descriptively: `2024-01-15-auth-decision.md`
3. Working files are gitignored; only templates are committed

## Templates

- @.agents/scratch/decisions/_template.md - For architectural decisions
- @.agents/scratch/notes/_template.md - For general notes
- @.agents/scratch/context/_template.md - For session context
- @.agents/scratch/research/_template.md - For research notes

