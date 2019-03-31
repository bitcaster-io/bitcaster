import pytest

from bitcaster.models import Address

pytestmark = pytest.mark.django_db


def test_address_str():
    addr = Address(label='label', address='address')
    assert str(addr)


def test_address_verified():
    addr = Address(label='label', address='address')
    assert not addr.verified


def test_address_reset_verified(user1):
    addr = Address(user=user1, label='label', address='address', verified=True)
    addr.save()
    assert addr.verified
    addr.address = 'new_address'
    addr.save()
    assert not addr.verified
