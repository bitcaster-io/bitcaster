import pytest

from bitcaster.models import Address, AddressAssignment

pytestmark = pytest.mark.django_db


def test_addressassignment():
    addr = AddressAssignment(address=Address(address='address', label='label'))
    assert str(addr) == 'label'
