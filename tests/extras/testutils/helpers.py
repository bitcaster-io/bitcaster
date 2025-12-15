from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from django.contrib.messages.storage.base import Message
    from django_webtest import DjangoWebtestResponse


def assert_form_error(response: "DjangoWebtestResponse", field: str, error: str) -> None:
    target = response.context["adminform"].form
    assert field in target.errors, f"No errors found for field '{field}'"
    assert error in target.errors[field], (
        f"Error message '{error}' not found for field '{field}'. Found {target.errors[field]}"
    )


def assert_message(response: "DjangoWebtestResponse", message: str, level: int | None = None) -> None:
    m: Message
    messages = list(response.context["messages"])
    for m in messages:
        if m.message == message:
            if level and level == m.level:
                return
            return
    pytest.fail(f"'{message}' not found")
