from __future__ import annotations

import contextlib

import pytest


@pytest.fixture(autouse=True)
def clear_state() -> None:
    from bitcaster.state import state

    with contextlib.suppress(AttributeError):
        del state.app
