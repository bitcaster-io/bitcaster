import os
from pathlib import Path
from unittest import mock
from unittest.mock import Mock

from pytest_django.fixtures import SettingsWrapper

from bitcaster.checks import (
    E002,
    E003,
    check_agent_validator,
    check_agent_validator_root,
)


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
