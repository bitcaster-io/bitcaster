import pytest

from bitcaster.models import OrganizationMember


@pytest.mark.django_db
def test_create():
    m = OrganizationMember(email='email@example.com')
    assert str(m)
