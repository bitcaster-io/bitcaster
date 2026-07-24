# Docker Integration Tests

This directory contains integration tests for the Bitcaster Docker image.
Tests validate both the image structure (Python version, installed packages,
user/group setup) and the running server (uWSGI process, healthcheck, HTTP
responses).

## Libraries

- **[pytest](https://docs.pytest.org/):** Test framework.
- **[pytest-docker](https://github.com/avast/pytest-docker):** Manages the
  Docker Compose lifecycle. Spins up the full stack (app + PostgreSQL + Redis)
  defined in `stack-samples/develop/compose.yml` for the test session.
- **[pytest-testinfra](https://testinfra.readthedocs.io/):** Provides the
  `docker_container` and `started_server` fixtures to inspect Docker
  containers programmatically (run commands, check users/groups, test
  network services).

## Running

```bash
# Run the tests (image is built automatically by compose)
pytest tests/ --test-docker --no-cov -vv  --capture no
```
