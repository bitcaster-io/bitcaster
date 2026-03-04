import pathlib
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from django.contrib.messages.storage.base import Message
    from django_webtest import DjangoWebtestResponse


def get_resource(path: str | pathlib.Path) -> pathlib.Path:
    return pathlib.Path(__file__).parent.parent.parent / pathlib.Path(path)


def assert_form_error(response: "DjangoWebtestResponse", field: str, error: str, partial: bool = False) -> None:
    target = response.context["adminform"].form
    assert field in target.errors, f"No errors found for field '{field}'"
    if partial:
        for err in target.errors[field]:
            if error in err:
                return
        pytest.fail(f"Error message '{error}' not found for field '{field}'. Found {target.errors[field]}")
    else:
        assert error in target.errors[field], (
            f"Error message '{error}' not found for field '{field}'. Found {target.errors[field]}"
        )


def assert_message(response: "DjangoWebtestResponse", message: str, level: int | None = None) -> None:
    m: Message
    messages = list(response.context["messages"])
    for m in messages:
        if message in m.message:
            if level and level == m.level:
                return
            return
    pytest.fail(f"'{message}' not found. {messages}")
