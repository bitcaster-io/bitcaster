from typing import Any

from bitcaster.constants import Bitcaster, SystemEvent


def test_trigger_event(system_objects: Any):
    o = Bitcaster.trigger_event(SystemEvent.OCCURRENCE_SILENCE)
    assert o.pk


def test_app(system_objects: Any, django_assert_num_queries: Any):
    with django_assert_num_queries(1):
        assert (a := Bitcaster.app)
    assert a.name == Bitcaster.APPLICATION

    with django_assert_num_queries(0):
        assert Bitcaster.app
