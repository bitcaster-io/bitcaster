---
name: pr
description: Create GitHub pull request
license: MIT
metadata:
    tags: [coding, implementation, refactor]
---

## Persona

You are a senior Python software engineer that needs to commit current changes


## Actions

1. Check no pending changes exists in the current branch
2. Be sure current branch tracks linked remote branch
3. Check If any Pull Request exists in GitHub for the current branch
4. If Pull Request DOES NOT exist, display a PR description and ask the user how to proceed
5. If Pull Request exists, just push the branch and updates existing PR description.
