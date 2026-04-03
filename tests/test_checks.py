import os
from pathlib import Path
from typing import TYPE_CHECKING
from unittest import mock
from unittest.mock import Mock

import pytest
from requests import HTTPError

from bitcaster.checks import (
    E002,
    E003,
    W001,
    W002,
    check_agent_validator,
    check_agent_validator_root,
    check_sentry,
)

if TYPE_CHECKING:
    from pytest_django.fixtures import SettingsWrapper


def test_check_agent_validator(settings: "SettingsWrapper") -> None:
    settings.AGENT_FILESYSTEM_VALIDATOR = lambda s: True
    check_agent_validator(Mock())

    settings.AGENT_FILESYSTEM_VALIDATOR = "bitcaster.agents.fs.validate_path"
    check_agent_validator(Mock())


def test_check_agent_validator_root(settings: "SettingsWrapper") -> None:
    settings.AGENT_FILESYSTEM_ROOT = str(Path(__file__).parent)
    assert check_agent_validator_root(Mock()) == []

    settings.AGENT_FILESYSTEM_ROOT = str(Path(__file__))
    assert check_agent_validator_root(Mock()) == [E002]

    settings.AGENT_FILESYSTEM_ROOT = "dir"
    with mock.patch.dict(os.environ, {"AGENT_FILESYSTEM_ROOT": "dir"}):
        assert check_agent_validator_root(Mock()) == [E003]


@pytest.mark.parametrize(
    ("value", "expected"),
    (  # noqa: PT007
        pytest.param("", [], id="no dsn"),
        pytest.param("--", [W001], id="wrong dsn"),
        pytest.param("https://error@test.sentry-server.io/123", [W002], id="http error"),
        pytest.param("https://sucess@test.sentry-server.io/123", [], id="valid dsn"),
    ),
)
def test_check_sentry(settings: "SettingsWrapper", value, expected) -> None:
    settings.SENTRY_DSN = value

    def mocked_capture_message(*args, **kwargs):
        if "error" in value:
            raise HTTPError()
        return True

    with mock.patch("sentry_sdk.capture_message", mocked_capture_message):
        assert check_sentry(Mock()) == expected
