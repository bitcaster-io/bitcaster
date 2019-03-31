import pytest

from bitcaster.models import Application
from bitcaster.security import ROLES
from bitcaster.utils.tests.factories import (ApplicationFactory,
                                             ApplicationMemberFactory,
                                             OrganizationMemberFactory,)


def test_application():
    app = Application(name='App1')
    assert str(app)


@pytest.mark.django_db
def test_application_channels(channel1):
    assert channel1.application.channels


@pytest.mark.django_db
def test_application_create():
    assert ApplicationFactory()


@pytest.mark.django_db
def test_application_create_slug(organization1):
    app = Application(organization=organization1, slug='abc')
    app.save()
    assert app.slug == 'abc'


# @pytest.mark.django_db
# def test_application_admins(team1):
#     assert list(team1.application.admins)


@pytest.mark.django_db
def test_application_owners(application1):
    assert application1.owners


@pytest.mark.django_db
def test_application_members(application1):
    o = OrganizationMemberFactory(organization=application1.organization)
    m = ApplicationMemberFactory(application=application1, org_member=o)
    assert list(application1.members) == [m.user]
    assert [ms.user for ms in application1.memberships.all()] == [m.user]


@pytest.mark.django_db
def test_application_membership(application1):
    o = OrganizationMemberFactory(organization=application1.organization)
    m = ApplicationMemberFactory(application=application1, org_member=o)
    assert list(application1.memberships.all()) == [m]


@pytest.mark.django_db
def test_application_admins(application1):
    o = OrganizationMemberFactory(organization=application1.organization)
    m = ApplicationMemberFactory(application=application1, org_member=o, role=ROLES.ADMIN)
    assert list(application1.admins) == [m.user]
