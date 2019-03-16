import pytest

pytestmark = pytest.mark.django_db


def test_str(role1):
    assert str(role1)


def test_members(role1):
    assert str(role1.members)
