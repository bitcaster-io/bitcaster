import pytest

from bitcaster.models import ApplicationUser


@pytest.mark.django_db
def test_application(organization_member):
    app = ApplicationUser(org_member=organization_member)
    assert str(app)
