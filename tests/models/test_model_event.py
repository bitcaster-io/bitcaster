from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models import Event


def test_model_event(event: "Event"):
    assert event.trigger({})
