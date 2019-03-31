import pytest

from bitcaster.models import ApplicationMember


@pytest.mark.django_db
def test_application(organization_member):
    app = ApplicationMember(org_member=organization_member)
    assert str(app)
