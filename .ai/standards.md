# Technical Standards

## Environment
- **Python:** 3.13 only (`requires-python = "==3.13.*"` in pyproject.toml)
- **Package Manager:** `uv` — virtualenv must be `.venv` (see `.envrc`)
- **Django settings:** `bitcaster.config.settings` (uses `django-environ`, reads from env vars)
- **Frameworks:** Django 5.2+, Dramatiq, DRF
- **Language:** British English for all text, comments, and identifiers (`colour`, `initialise`)

## Coding Mandates
- **Type Safety:** Mandatory type hints for all new functions. Use `django-stubs` patterns.
- **Type Syntax:** Do not use Python <3.9 syntax. Use `list` not `List`, `dict` not `Dict`.
- **Asynchronous First:** All delivery logic, external API calls, and heavy processing MUST be offloaded to Dramatiq tasks (`src/bitcaster/runner/`). Never perform synchronous network operations in the request-response cycle.
- **Multi-tenancy:** Strictly enforce Organisation/Project level isolation in all database queries. See `.ai/domain.md` for the model hierarchy and access control patterns.
- **Relative Imports:** Use relative imports within `src/bitcaster/`, not absolute imports.
- **Logging:** Use `logger = logging.getLogger(__name__)` — never `print()`
- **Patterns:** Strictly respect following paradigms/patterns
  - Twelve Factor
  - SOLID: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
  - DRY: Don't Repeat Yourself

## Linting & Format
- **Ruff:** `ruff.toml` — line-length 120, double quotes, custom isort sections (django, testing)
- **djlint:** `djlint.toml` — profile django, indent 4, max line 120
- **mypy:** `mypy.ini` — strict mode, `django-stubs` plugin, `bitcaster.config.settings` as django settings module
- **Command:** `tox -e lint` (ruff + pre-commit hooks)
