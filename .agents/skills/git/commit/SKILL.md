---
name: commit
description: Commit changes
license: MIT
metadata:
    tags: [coding, implementation, refactor]
---

You are a senior Python software engineer that needs to commit current changes

## Action

1. Add all changed files except "alien", "not relevant", "private" or "temporary" ones
2. Be sure no  "alien", "not relevant", "private" or "temporary" have been added for commit
3. Analyze the intent checking the diff
4. Be sure you are not in "develop" but in a dedicated branch. Halt otherwise
5. If it is not in a dedicated branch, ask the user top create a new one and move all changes there before proceed
5. Be sure `tox` do not have any issue otherwise, fix them and repeat until `tox` succeed

## Output

- display list of files will be commited like
    ```
    modified:  docs/adm-guide/dispatchers/.pages  # Added X to dispatcher nav
    new:       docs/adm-guide/dispatchers/x.md    # X dispatcher admin guide
    ...
    ```
- display commit message
- ask user for further steps
