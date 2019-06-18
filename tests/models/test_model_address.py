import pytest

from bitcaster.models import Address

pytestmark = pytest.mark.django_db


def test_address_str():
    addr = Address(label='label', address='address')
    assert str(addr)


def test_address_reset_verified(user1):
    addr = Address(user=user1, label='label', address='address')
    addr.save()
