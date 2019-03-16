import pytest

from bitcaster.models import OrganizationMember


@pytest.mark.django_db
def test_create(admin_user):
    m = OrganizationMember(user=admin_user)
    assert str(m)
