import pytest

from bitcaster.models import User

pytestmark = pytest.mark.django_db


def test_str(user1):
    assert str(user1)


def test_add_token(user1, application1):
    assert user1.add_token(application1)


def test_send_confirmation_email(user1):
    assert user1.send_confirmation_email()


# UserManager


def test_create_user():
    assert User.objects.create_user('a@b.com', '123')


def test_create_superuser():
    assert User.objects.create_superuser('a@b.com', '123')
