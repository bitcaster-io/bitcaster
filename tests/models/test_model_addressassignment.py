import pytest

from bitcaster.models import Address, AddressAssignment
from bitcaster.utils.tests.factories import ChannelFactory

pytestmark = pytest.mark.django_db


def test_addressassignment():
    addr = AddressAssignment(address=Address(address='address', label='label'),
                             channel=ChannelFactory(name='Channel1'))
    assert str(addr) == 'Channel1 (label)'


def test_address_verified():
    addr = AddressAssignment(address=Address(address='address', label='label'),
                             channel=ChannelFactory())
    assert not addr.verified
