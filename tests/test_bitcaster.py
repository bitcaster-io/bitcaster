from bitcaster.constants import Bitcaster, SystemEvent


def test_trigger_event(system_events):
    o = Bitcaster.trigger_event(SystemEvent.OCCURRENCE_SILENCE)
    assert o.pk


def test_app(system_events, django_assert_num_queries):
    with django_assert_num_queries(1):
        assert (a := Bitcaster.app)
    assert a.name == Bitcaster.APPLICATION

    with django_assert_num_queries(0):
        assert Bitcaster.app
