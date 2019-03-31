import pytest

from bitcaster.models import OrganizationGroup


@pytest.mark.django_db
def test_create(admin_user):
    m = OrganizationGroup(name='group1')
    assert str(m)
