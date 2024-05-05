import uuid
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from bitcaster.models import Event, Occurrence


def test_event_trigger(event: "Event"):
    assert event.trigger({})


@pytest.mark.parametrize(
    "cid",
    [
        uuid.UUID("3f430b9b-ca28-43a3-bad0-954d20f35c37"),
        "cf09bfc574554e3a9619a69021936bcb",
        "ffe1b3e8-0fcd-42b5-8ccd-7304715b329d",
    ],
)
def test_trigger_correlation_id(event: "Event", cid: str):
    o: "Occurrence" = event.trigger({}, options={}, cid=cid)
    assert o.correlation_id == str(cid)
