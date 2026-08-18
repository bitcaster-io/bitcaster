# Creating a New Dispatcher

A **Dispatcher** is the component in Bitcaster responsible for the physical delivery of a message to a specific destination (e.g., sending an Email via SMTP, a message via Slack Webhook, or an SMS via Twilio).

---

## 1. Anatomy of a Dispatcher

Every dispatcher must inherit from `bitcaster.dispatchers.base.Dispatcher` and implement the core delivery logic.

### File Structure
Place your new dispatcher in `src/bitcaster/dispatchers/my_service.py`.

### Basic Implementation

```python
from typing import Any
from django import forms
from bitcaster.dispatchers.base import Dispatcher, DispatcherConfig, MessageProtocol, Payload
from bitcaster.models import Assignment

class MyServiceConfig(DispatcherConfig):
    # Define the fields required to configure this dispatcher
    api_key = forms.CharField(help_text="Your Service API Key")
    region = forms.ChoiceField(choices=[('us', 'USA'), ('eu', 'Europe')])

class MyServiceDispatcher(Dispatcher):
    slug = "my-service"            # Unique identifier
    verbose_name = "My Service"    # Name displayed in the UI
    config_class = MyServiceConfig # The form used for configuration
    protocol = MessageProtocol.SMS # Protocol (defines capabilities like HTML support)

    def _send(self, address: str, payload: Payload, assignment: Assignment | None = None, **kwargs: Any) -> bool:
        """
        Core logic to send the message.
        - address: The destination (phone number, email, etc.)
        - payload: Payload dataclass with strongly typed fields (.message, .subject, .html_message). Follow django-stubs.
        - self.config: Dictionary containing validated data from MyServiceConfig
        """
        api_key = self.config['api_key']
        # Call your external API here...
        # If success, return True. If failure, Bitcaster will handle logging.
        return True
```

---

## 2. Key Attributes

- **`slug`**: A unique string used to identify the dispatcher in the database.
- **`protocol`**: Use `MessageProtocol.EMAIL`, `SMS`, `SLACK`, `WEBPUSH`, etc. This tells Bitcaster if the dispatcher supports subjects or HTML.
- **`config_class`**: A Django Form class. Bitcaster uses this to render the configuration UI for each Channel.
- **`address_types`**: Defines what kind of addresses this dispatcher can handle (e.g., `AddressType.EMAIL`).

---

## 3. Registration

Bitcaster uses a **Registry** pattern. Simply by inheriting from `Dispatcher` and ensuring the file is imported, the dispatcher will be automatically registered and available in the UI.

Ensure your module is imported in `src/bitcaster/dispatchers/__init__.py`:
```python
from .my_service import MyServiceDispatcher
```

---

## 4. Writing Tests

Bitcaster emphasizes testing for all dispatchers to ensure reliability.

### Create a Test File
Create `tests/dispatchers/test_my_service.py`.

### Example Test
Use the `Dispatcher` base testing patterns and mock external API calls.

```python
import pytest
from unittest.mock import patch
from bitcaster.dispatchers.my_service import MyServiceDispatcher

def test_myservice_send(channel_factory):
    # 1. Setup a channel with proper config
    config = {'api_key': 'secret', 'region': 'eu'}
    channel = channel_factory(dispatcher="my-service", config=config)
    dispatcher = MyServiceDispatcher(channel)

    # 2. Prepare a payload
    from bitcaster.dispatchers.base import Payload
    payload = Payload(message="Hello World", event=channel.application.events.first())

    # 3. Mock the external service and test
    with patch('my_service_sdk.send_message') as mock_send:
        mock_send.return_value = True
        success = dispatcher.send("test-address", payload)

        assert success is True
        mock_send.assert_called_once()
```

### Run the Tests
```bash
pytest tests/dispatchers/test_my_service.py
```

---

## 6. Email Dispatchers with AnyMail

Email dispatchers that use the [django-anymail](https://github.com/anymail/django-anymail) library
can share a common base instead of implementing `_send` from scratch.

### File Structure

Place your dispatcher in `src/bitcaster/dispatchers/anymail/my_service.py` and export it in both
`anymail/__init__.py` and `dispatchers/__init__.py`.

### Basic Implementation

```python
from anymail.backends.my_service import EmailBackend
from django import forms
from .base import AnyMailDispatcher, AnyMailConfig
from ..base import DispatcherConfig

class MyServiceConfig(DispatcherConfig):
    api_key = forms.CharField(label="API Key")
    # Optional fields, or inherit from AnyMailConfig for api_key + sender_domain

class MyServiceDispatcher(AnyMailDispatcher):
    slug = "my-service"
    verbose_name = "My Service Email"
    config_class = MyServiceConfig
    backend = EmailBackend
```

### Customising the Connection

Override `get_connection()` if the backend needs extra kwargs:

```python
def get_connection(self) -> DispatcherHandler:
    kwargs = {"api_key": self.config["api_key"]}
    return self.backend(fail_silently=False, **kwargs)
```

### Customising the From Address

Override `get_from_email()` if you need per-dispatcher sender logic:

```python
def get_from_email(self) -> str:
    from_email = self.config.get("from_address") or self.channel.from_email
    from_label = self.config.get("from_label") or ""
    if from_label:
        from_email = f"{from_label} <{from_email}>"
    return from_email
```

---

## 5. Best Practices

1. **Error Handling**: Do not catch all exceptions in `_send`. If an unhandled exception occurs, Bitcaster will catch it, log it, and mark the delivery as failed.
2. **British English**: Use British English for comments and UI messages (e.g., "Colour", not "Color").
3. **Type Hinting**: Always use type hints for all methods and ensure compliance with `django-stubs`.
4. **Validation**: Use the `clean()` method in your `DispatcherConfig` form to perform complex validation (e.g., verifying an API key format).
