import uuid
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from bitcaster.models import Event, Occurrence


def test_event_trigger(event: "Event"):
    assert event.trigger({})


@pytest.mark.parametrize("cid", [uuid.uuid4(), uuid.uuid4().hex, str(uuid.uuid4())])
def test_trigger_correlation_id(event: "Event", cid: str):
    o: "Occurrence" = event.trigger({}, cid)
    assert o.correlation_id == str(cid)
