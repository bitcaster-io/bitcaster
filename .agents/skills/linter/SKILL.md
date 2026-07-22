---
name: linter
description: Lint and test code to complete the PR
license: MIT
metadata:
    tags: [coding, implementation, refactor]
---

## Persona

You are a senior Python software developer


## Purpose

- make all code compliant with the project code-conventions
- update/fix existing tests
- check the coverage

## Actions

1. run `git add -a`
2. run `tox -e format`
3. run `tox -e lint`, check the output and fix all issues found, repeat until success
4. run `tox -e mypy`, check the output and fix all issues found, repeat until success
5. run `tox -e tests`, check the output and fix all issues and coverage, repeat until success
6. Check all documentation for any misalignment with the code, conflicting text and
