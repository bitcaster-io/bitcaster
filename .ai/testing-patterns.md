# Testing Patterns: Factories & Fixtures

This document enforces Bitcaster's testing standards, ensuring a strict separation of concerns between model generation and test data provision.

## Core Mandates

1. **Isolation:** NEVER use `Factory` classes directly within a test function.
2. **Layering:** Use `factory-boy` to define low-level database objects. Factories are located in `tests/extras/testutils/factories`.
3. **Wrapping:** Tests MUST use `pytest` fixtures that wrap these Factory instances, customising them for specific scenarios.
4. **Consistency:** Fixtures should be clear, specific, and defined in the same test file that uses them.
5. **Reusability:** Common fixtures can reside in `conftest.py` if they are reused across multiple modules.

## Implementation Pattern

### 1. Define the Factory
Factories are for low-level registration. Use `AutoRegisterModelFactory`.

```python
class UserFactory(AutoRegisterModelFactory[User]):
    class Meta:
        model = User
```

### 2. Define the Fixture
Fixtures "wrap" the factory. Use `Factory.create()` to ensure proper type hinting for `mypy`.

```python
@pytest.fixture
def user() -> "User":
    """Standard user fixture."""
    from testutils.factories import UserFactory
    return UserFactory.create()
```

## Best Practices
- **Importing:** Avoid importing Django models or Factories at the module level in test files to prevent premature Django initialisation. Import them inside the fixture function or use `if TYPE_CHECKING`.
- **Customisation:** Use the `configure_model` context manager for minor object adjustments within a test instead of creating multiple similar fixtures.
