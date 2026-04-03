from typing import TYPE_CHECKING

import pytest
from exceptiongroup import suppress

from bitcaster.utils.sentry import init_sentry

if TYPE_CHECKING:
    from pytest_django.fixtures import SettingsWrapper


@pytest.mark.parametrize("raise_exception", [True, False])
def test_init_sentry_fail(settings: "SettingsWrapper", raise_exception) -> None:
    settings.SENTRY_DSN = "-"

    with suppress(Exception):
        assert not init_sentry(raise_exception)


def test_init_sentry_success(settings: "SettingsWrapper") -> None:
    settings.SENTRY_DSN = ""

    assert init_sentry(False)
