import pytest

pytestmark = pytest.mark.django_db


def test_str(subscription1):
    assert str(subscription1)


def test_recipient(subscription1):
    assert str(subscription1.recipient)


def test_register_error(subscription1):
    assert subscription1.register_error()
    assert subscription1.errors
    log = subscription1.error_log.latest()
    assert log.application == subscription1.event.application
