from unittest.mock import Mock

from pytest_django.fixtures import SettingsWrapper

from bitcaster.checks import check_agent_validator


def test_check_agent_validator(settings: "SettingsWrapper") -> None:
    settings.AGENT_FILESYSTEM_VALIDATOR = lambda s: True
    check_agent_validator(Mock())

    settings.AGENT_FILESYSTEM_VALIDATOR = "bitcaster.agents.fs.validate_path"
    check_agent_validator(Mock())
