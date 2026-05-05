import os

from unittest import mock

from bitcaster.config.fragments.logging import _apply_dynamic_logging_levels


def test_apply_dynamic_logging_levels_new_logger():
    logging_dict = {"loggers": {"existing": {"level": "INFO"}}}
    # Using double underscore to map to dot
    with mock.patch.dict(os.environ, {"LOGGING_LEVEL_NEW__LOGGER": "DEBUG"}):
        _apply_dynamic_logging_levels(logging_dict)

    assert "new.logger" in logging_dict["loggers"]
    assert logging_dict["loggers"]["new.logger"]["level"] == "DEBUG"
    assert logging_dict["loggers"]["new.logger"]["handlers"] == ["console"]


def test_apply_dynamic_logging_levels_existing_logger():
    logging_dict = {"loggers": {"existing": {"level": "INFO"}}}
    with mock.patch.dict(os.environ, {"LOGGING_LEVEL_EXISTING": "ERROR"}):
        _apply_dynamic_logging_levels(logging_dict)

    assert logging_dict["loggers"]["existing"]["level"] == "ERROR"
