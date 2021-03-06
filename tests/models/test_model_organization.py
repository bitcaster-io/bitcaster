import pytest

from bitcaster.framework.db.fields import ORG_ROLES
from bitcaster.models import Organization
from bitcaster.utils.tests.factories import OrganizationFactory

pytestmark = pytest.mark.django_db


def test_str(organization1):
    assert str(organization1)


def test_invitations(organization1):
    assert organization1.invitations


def test_delete_fail_if_core():
    org = OrganizationFactory(is_core=True)
    with pytest.raises(Exception):
        org.delete()


def test_delete():
    org = OrganizationFactory(is_core=False)
    org.delete()


def test_create(user1):
    app = Organization(owner=user1, slug='abc')
    app.save()
    assert app.slug == 'abc'


def test_application_no_admins(organization1):
    assert list(organization1.supervisors) == []


def test_supervisors(organization1, user1):
    organization1.add_member(user1, ORG_ROLES.SUPERVISOR)
    assert list(organization1.supervisors) == [user1]


def test_managers(organization1, user1):
    organization1.add_member(user1, ORG_ROLES.SUPERVISOR)
    assert list(organization1.managers) == [user1]


def test_owners(organization1):
    assert list(organization1.owners) == [organization1.owner]
