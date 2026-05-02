# System Architecture

## Project Layout
- `src/bitcaster/`: Core application logic.
    - `admin/`: Admin endpoints and serializers.
    - `agents/`: Internal execution agents.
    - `api/`: DRF endpoints and serializers.
    - `config/`: Application configuration and settings.
    - `dispatchers/`: Delivery channel implementations.
    - `models/`: Database schemas.
    - `runner/`: Dramatiq background task definitions.
- `tests/`: Project test suite (mirrors `src/` structure).
- `docs/`: MkDocs source files.

## Patterns & Anti-Patterns
- **Testing:** Use `factory-boy` for generating test data.
- **Production Safety:** NEVER use `factory-boy` factories outside of testing environments.
- **Modularity:** Prefer composition over complex inheritance for dispatchers and agents.
