import pytest

pytestmark = pytest.mark.django_db


def test_str(team1):
    assert str(team1)


def test_recipient(subscription1):
    assert str(subscription1.recipient)


def test_members(team1):
    assert list(team1.members)
