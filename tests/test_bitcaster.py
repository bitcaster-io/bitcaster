from bitcaster.constants import Bitcaster, SystemEvent


def test_trigger_event(system_events):
    o = Bitcaster.trigger_event(SystemEvent.OCCURRENCE_SILENCE)
    assert o.pk
