# Workflow & Lifecycle

## Build & Verify Commands
```bash
uv sync                    # install deps (uses uv.lock)
tox -e lint               # ruff + pre-commit hooks (run first)
tox -e mypy               # type checking (strict mode, mypy.ini)
tox -e tests              # pytest with coverage
tox -e tests -- -k "test_name"  # single test
```

## Development Flow
- **Base Branch:** Feature branches should start from the `develop` branch.
- **Bug Fixes:**
    1. Identify the affected version/branch.
    2. Write a failing test case that reproduces the reported issue.
    3. Apply the fix and ensure all tests pass.

## Validation Protocol
- **Patch Coverage:** 100% patch coverage is mandatory — `diff-cover` compares against `origin/develop`
- **Required Checks:** Before finishing any task, you must run:
    - `tox -e lint`: For code style and linting.
    - `tox -e mypy`: For static type checking.
    - `tox -e tests`: To ensure no regressions (includes diff-cover check).
    - `tox -e docs`: If documentation or docstrings are modified.

## CI Notes
- Lint runs on push to `develop` and PRs (draft PRs skipped)
- Tests need Postgres + Redis services (see `.github/workflows/test.yml`)
