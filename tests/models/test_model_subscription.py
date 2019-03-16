import pytest

pytestmark = pytest.mark.django_db


def test_str(subscription1):
    assert str(subscription1)


def test_recipient(subscription1):
    assert str(subscription1.recipient)
