# System Architecture

## Project Layout
- `src/bitcaster/`: Core application logic (src layout).
    - `admin/`: Admin endpoints and serializers.
    - `agents/`: Internal execution agents.
    - `api/`: DRF endpoints and serializers.
    - `config/`: Application configuration and settings.
    - `dispatchers/`: Delivery channel implementations.
    - `models/`: Database schemas.
    - `runner/`: Dramatiq background task definitions.
- `tests/`: Project test suite (mirrors `src/` structure).
- `docs/`: MkDocs source files.

## Code Structure Rules
- **Src layout:** Code in `src/bitcaster/`, tests mirror structure in `tests/`
- **Imports:** Use relative imports within `src/bitcaster/`, not absolute imports

## Patterns & Anti-Patterns
- **Testing:** Use `factory-boy` for generating test data.
- **Production Safety:** NEVER use `factory-boy` factories outside of testing environments.
- **Modularity:** Prefer composition over complex inheritance for dispatchers and agents.
