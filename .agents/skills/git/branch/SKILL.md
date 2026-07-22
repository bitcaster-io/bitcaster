---
name: branch
description: Create a new branch for pending changes
license: MIT
metadata:
    tags: [git]
compatibility: opencode
---

## Persona
Expert Python Engineer

## Context
pending changes in the current git managed folder (both stanged/unstaged).

## Steps

1. Analyze the intent of the diff (fix, feat, refactor, chore).
2. Propose a kebab-case branch name (max 40 chars).
3. add all pending changes with `git add .`
4. stash all pending changes with `git stash`
5. pull all remote changes with `git pull`
7. create the new branch from develop and move to it

## Notes

  - uses  --no-pager  options for git to avoid user interaction
  - git command are allowed
