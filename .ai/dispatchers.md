# Dispatcher Development Guide

This guide covers the creation and configuration of new Dispatchers (SMS, Webhooks, Push, etc.) in Bitcaster.

## Core Mandates

1. **Inheritance:** All dispatchers MUST inherit from `bitcaster.dispatchers.base.Dispatcher`.
2. **Configuration:** Every dispatcher MUST define a `config_class` inheriting from `DispatcherConfig` (based on Django Forms).
3. **Protocol:** Assign the correct `MessageProtocol` to define channel capabilities (HTML, TEXT, SUBJECT, etc.).
4. **Validation:** Handle delivery errors in `_send` by raising `bitcaster.exceptions.DispatcherError`.
5. **Testing:** Every dispatcher MUST have a corresponding test file in `tests/dispatchers/test_d_<slug>.py`.
6. **Documentation**:  Every dispatcher MUST be properly documented in its own page and listed in the README.md

## Implementation Workflow

### 1. Dispatcher Class Structure
```python
from typing import Any
from django import forms
from .base import Dispatcher, MessageProtocol, Payload, DispatcherConfig
from ..exceptions import DispatcherError


class MyDispatcherConfig(DispatcherConfig):
    key = forms.CharField()


class MyDispatcher(Dispatcher):
    slug = "my-dispatcher"
    verbose_name = "Service Name"
    config_class = MyDispatcherConfig
    protocol = MessageProtocol.PLAINTEXT

    def _send(self, address: str, payload: Payload, **kwargs: Any) -> bool:
        try:
            # Access validated configuration via self.config
            # Execute delivery logic
            return True
        except Exception as e:
            raise DispatcherError(f"Error during delivery: {e}") from e
```

## Related Resources
- `src/bitcaster/dispatchers/base.py`: Base class and protocol definitions.
- `tests/dispatchers/`: Existing dispatcher tests for reference.
