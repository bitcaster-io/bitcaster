# Technical Standards

## Environment
- **Python:** 3.13 (Strict).
- **Package Manager:** `uv` (Virtualenvs must be in `.venv`).
- **Frameworks:** Django 5.2+, Dramatiq, DRF.

## Coding Mandates
- **Type Safety:** Mandatory type hints for all new functions. Use `django-stubs` patterns.
- **Asynchronous First:** All delivery logic, external API calls, and heavy processing MUST be offloaded to Dramatiq tasks. Never perform synchronous network operations in the request-response cycle.
- **Multi-tenancy:** Strictly enforce Organization/Project level isolation in all database queries.
