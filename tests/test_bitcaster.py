from typing import TYPE_CHECKING, Any

from bitcaster.constants import SystemEvent, bitcaster

if TYPE_CHECKING:
    from bitcaster.models import Application


def test_trigger_event(system_objects: Any) -> None:
    o = bitcaster.trigger_event(SystemEvent.OCCURRENCE_SILENCE)
    assert o.pk


def test_app(system_objects: Any, django_assert_num_queries: Any) -> None:
    a: "Application"
    with django_assert_num_queries(1):
        assert (a := bitcaster.app)
    assert a.name == bitcaster.APPLICATION

    with django_assert_num_queries(0):
        assert bitcaster.app
