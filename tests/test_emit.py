import pytest

from bitcaster.exceptions import LogicError
from bitcaster.tasks import emit_event


@pytest.mark.django_db
def test_base(event1):
    assert emit_event(event1, {}) == (0, 0)


@pytest.mark.django_db
def test_subscription1(subscription1):
    event = subscription1.event
    assert emit_event(event, {}) == (1, 0)


@pytest.mark.django_db
def test_disabled_event(subscription1):
    subscription1.event.enabled = False
    subscription1.event.save()
    event = subscription1.event
    with pytest.raises(LogicError):
        assert emit_event(event, {}) == (0, 0)


@pytest.mark.django_db
def test_disabled_event_with_ignore_disabled(subscription1):
    subscription1.event.enabled = False
    subscription1.event.save()
    event = subscription1.event
    assert emit_event(event, {}, ignore_disabled=True) == (1, 0)
