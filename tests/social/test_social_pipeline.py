from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest
from constance.test.unittest import override_config
from social_core.backends.base import BaseAuth
from social_core.exceptions import AuthForbidden
from social_django.models import DjangoStorage

from bitcaster.social.pipeline import add_email_address, create_user, save_to_group
from bitcaster.social.strategy import BitcasterStrategy

if TYPE_CHECKING:
    from django.contrib.auth.models import Group

    from bitcaster.models import User


@pytest.fixture
def group(db: Any) -> None:
    from testutils.factories import GroupFactory

    GroupFactory(name="demo")


@override_config(NEW_USER_DEFAULT_GROUP="demo")  # type: ignore[misc]
def test_save_to_group(group: "Group", user: "User") -> None:
    save_to_group(Mock(), user, is_new=True)
    assert user.groups.first().name == "demo"
    assert save_to_group(Mock(), None, is_new=False) == {}


def test_add_email_address1(group: "Group", user: "User") -> None:
    add_email_address(Mock(), user=user, is_new=False)


def test_add_email_address2(group: "Group", user: "User") -> None:
    add_email_address(Mock(), user=user, is_new=True)


@override_config(SOCIAL_AUTH_CREATE_USER=True)
def test_social_create_user1() -> None:
    s = BitcasterStrategy(storage=DjangoStorage)
    u = create_user(
        strategy=s,
        details={
            "username": "test",
            "email": "email@example.com",
            "first_name": "first_name",
            "last_name": "last_name",
        },
        backend=BaseAuth(s),
    )
    assert u


@override_config(SOCIAL_AUTH_CREATE_USER=False)
def test_social_create_user2() -> None:
    s = BitcasterStrategy(storage=DjangoStorage)
    with pytest.raises(AuthForbidden):
        create_user(
            strategy=s,
            details={
                "username": "test",
                "email": "email@example.com",
                "first_name": "first_name",
                "last_name": "last_name",
            },
            backend=BaseAuth(s),
        )


@override_config(SOCIAL_AUTH_CREATE_USER=False)
def test_social_create_user3() -> None:
    s = BitcasterStrategy(storage=DjangoStorage)
    with pytest.raises(AuthForbidden):
        create_user(
            strategy=s,
            details={
                "username": "test",
                "first_name": "first_name",
                "last_name": "last_name",
            },
            backend=BaseAuth(s),
        )


@override_config(SOCIAL_AUTH_CREATE_USER=False)
def test_social_create_user4(user) -> None:
    s = BitcasterStrategy(storage=DjangoStorage)
    assert create_user(
        strategy=s,
        details={
            "username": user.username,
            "email": user.email,
            "first_name": "first_name",
            "last_name": "last_name",
        },
        backend=BaseAuth(s),
    )
