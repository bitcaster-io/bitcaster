import pytest

from bitcaster.models import User
from bitcaster.security import APP_ROLES
from bitcaster.utils.tests.factories import (ApplicationMemberFactory,
                                             OrganizationMemberFactory,)

pytestmark = pytest.mark.django_db


def test_str(user1):
    assert str(user1)


def test_add_token(user1, application1):
    assert user1.add_token(application1)


def test_send_confirmation_email(user1):
    assert user1.send_confirmation_email()


def test_is_manager(user1):
    o = OrganizationMemberFactory(user=user1)
    ApplicationMemberFactory(org_member=o,
                             application__organization=o.organization,
                             role=APP_ROLES.ADMIN)
    assert user1.is_manager


def test_store(user1):
    user1.store('ns', 'key', 1)
    assert user1.retrieve('ns', 'key') == 1


# UserManager


def test_create_user():
    assert User.objects.create_user('a@b.com', '123')


def test_create_superuser():
    assert User.objects.create_superuser('a@b.com', '123')
