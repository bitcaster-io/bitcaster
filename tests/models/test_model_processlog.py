from typing import TYPE_CHECKING

import pytest

from bitcaster.runner.tasks import delete_expired_user_messages

if TYPE_CHECKING:
    from bitcaster.models import ProcessLogEntry


def test_str(processlogentry: "ProcessLogEntry") -> None:
    assert str(processlogentry)


def test_natural_key(processlogentry) -> None:
    assert processlogentry.__class__.objects.get_by_natural_key(*processlogentry.natural_key()) == processlogentry


@pytest.mark.parametrize("error", [None, Exception()])
def test_manager_log_process(processlogentry, error) -> None:
    processlogentry.__class__.objects.log_process(actor=delete_expired_user_messages, error=error)
