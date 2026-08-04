from __future__ import annotations

from allauth.account.internal.flows.login import AUTHENTICATION_METHODS_SESSION_KEY

import pytest
from unittest.mock import MagicMock

from django.contrib.auth.models import AnonymousUser

from bitcaster.social.utils import is_own_login_provider

pytestmark = pytest.mark.django_db


@pytest.fixture
def provider():
    from testutils.factories import SocialProviderFactory

    return SocialProviderFactory.create(provider="google")


@pytest.fixture
def user():
    from testutils.factories import UserFactory

    return UserFactory.create()


def _request(user, session=None):
    request = MagicMock()
    request.user = user
    request.session = session or {}
    return request


def test_anonymous_user(provider):
    assert is_own_login_provider(_request(AnonymousUser()), provider) is False


def test_unrelated_user(user, provider):
    assert is_own_login_provider(_request(user), provider) is False


def test_session_authenticated_via_provider(user, provider):
    session = {
        AUTHENTICATION_METHODS_SESSION_KEY: [
            {"method": "socialaccount", "provider": str(provider.pk), "uid": "123"},
        ]
    }
    assert is_own_login_provider(_request(user, session), provider) is True


def test_session_authenticated_via_other_method(user, provider):
    session = {
        AUTHENTICATION_METHODS_SESSION_KEY: [
            {"method": "password", "username": user.username},
        ]
    }
    assert is_own_login_provider(_request(user, session), provider) is False


def test_session_authenticated_via_other_provider(user, provider):
    session = {
        AUTHENTICATION_METHODS_SESSION_KEY: [
            {"method": "socialaccount", "provider": str(provider.pk + 1), "uid": "123"},
        ]
    }
    assert is_own_login_provider(_request(user, session), provider) is False


def test_linked_social_account(user, provider):
    from testutils.factories import SocialAccountFactory

    SocialAccountFactory.create(user=user, provider=str(provider.pk))
    assert is_own_login_provider(_request(user), provider) is True


def test_social_account_linked_to_other_user(user, provider):
    from testutils.factories import SocialAccountFactory

    SocialAccountFactory.create(provider=str(provider.pk))
    assert is_own_login_provider(_request(user), provider) is False
