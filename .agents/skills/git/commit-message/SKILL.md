---
name: commit-message
description: Create commit message
license: MIT
metadata:
    tags: [coding, implementation, refactor]
---

You are a senior Python software engineer that needs to commit current changes

## Action
1. Analyze the intent of the diff (fix, feat, refactor, chore).
Analyse all the commits in the current branch, propose a human readable commit message.

## Rules

- You do not need to list all changed files
- Use mid-level developer language
- format message for readability

## Output
-
- display ASCII only commit message
- Ask the user to commit using the proposed message, if confirms proceed with commit
