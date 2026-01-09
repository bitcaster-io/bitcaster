import pytest

from bitcaster.models import LogEntry


def test_extra_action_flags() -> None:
    from testutils.factories import LogEntryFactory

    entry = LogEntryFactory(action_flag=LogEntry.OTHER, object_repr="Object")
    assert str(entry) == "”Object”."


@pytest.mark.parametrize("flag", [LogEntry.ADDITION, LogEntry.OTHER])
def test_action_flags(flag: str) -> None:
    from testutils.factories import LogEntryFactory

    entry = LogEntryFactory(action_flag=flag, object_repr="Object")
    assert str(entry)
