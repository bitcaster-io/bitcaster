# Workflow & Lifecycle

## Development Flow
- **Base Branch:** Feature branches should start from the `develop` branch.
- **Bug Fixes:**
    1. Identify the affected version/branch.
    2. Write a failing test case that reproduces the reported issue.
    3. Apply the fix and ensure all tests pass.

## Validation Protocol
- **Patch Coverage:** 100% patch coverage is mandatory (verified via `diff-cover`).
- **Required Checks:** Before finishing any task, you must run:
    - `tox -e lint`: For code style and linting.
    - `tox -e mypy`: For static type checking.
    - `tox -e tests`: To ensure no regressions.
    - `tox -e docs`: If documentation or docstrings are modified.
