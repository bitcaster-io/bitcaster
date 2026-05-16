from __future__ import annotations

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.models import SocialAccount, SocialLogin

import pytest
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import Group

from bitcaster.constants import AddressType
from bitcaster.social.adapter import BitcasterAccountAdapter, BitcasterSocialAccountAdapter


@pytest.mark.django_db
class TestBitcasterSocialAccountAdapter:
    @pytest.fixture
    def adapter(self):
        return BitcasterSocialAccountAdapter()

    @pytest.fixture
    def request_mock(self):
        return MagicMock()

    @pytest.fixture
    def google_provider(self):
        from testutils.factories import SocialProviderFactory

        return SocialProviderFactory.create(provider="google", client_id="test-client-id", secret="test-secret")

    @pytest.fixture
    def provider_with_legacy_config(self):
        from testutils.factories import SocialProviderFactory

        return SocialProviderFactory.create(
            provider="google",
            configuration={
                "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY": "legacy-id",
                "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET": "legacy-secret",
            },
        )

    @pytest.fixture
    def oidc_providers(self):
        from bitcaster.social.models import SocialProvider

        SocialProvider.objects.create(provider="openid_connect", label="First", client_id="first-client", enabled=True)
        SocialProvider.objects.create(
            provider="openid_connect", label="Second", client_id="second-client", enabled=True
        )

    @pytest.fixture
    def existing_user(self):
        from testutils.factories import UserFactory

        return UserFactory.create(email="test@example.com")

    def test_get_app_from_dedicated_fields(self, adapter, request_mock, google_provider):
        app = adapter.get_app(request_mock, "google")
        assert app.client_id == "test-client-id"
        assert app.secret == "test-secret"
        assert app.provider == "google"

    def test_get_app_legacy_compatibility(self, adapter, request_mock, provider_with_legacy_config):
        app = adapter.get_app(request_mock, "google")
        assert app.client_id == "legacy-id"
        assert app.secret == "legacy-secret"

    def test_is_auto_signup_allowed(self, adapter, request_mock):
        with patch("bitcaster.social.adapter.config") as mock_config:
            mock_config.SOCIAL_AUTH_CREATE_USER = True
            assert adapter.is_auto_signup_allowed(request_mock, MagicMock()) is True

            mock_config.SOCIAL_AUTH_CREATE_USER = False
            assert adapter.is_auto_signup_allowed(request_mock, MagicMock()) is False

    def test_is_open_for_signup_social_create_user_disabled(self, adapter, request_mock):
        sociallogin = MagicMock()
        sociallogin.user = MagicMock()
        with patch("bitcaster.social.adapter.config") as mock_config:
            mock_config.SOCIAL_AUTH_CREATE_USER = False
            assert adapter.is_open_for_signup(request_mock, sociallogin) is False

    def test_is_open_for_signup_social_accepted_users_match(self, adapter, request_mock):
        sociallogin = MagicMock()
        sociallogin.user = MagicMock()
        sociallogin.user.email = "allowed@example.com"
        with patch("bitcaster.social.adapter.config") as mock_config:
            mock_config.SOCIAL_AUTH_CREATE_USER = True
            mock_config.SOCIAL_AUTH_ACCEPTED_USERS = ".*@example.com, admin@bitcaster.io"
            assert adapter.is_open_for_signup(request_mock, sociallogin) is True

    def test_is_open_for_signup_social_accepted_users_no_match(self, adapter, request_mock):
        sociallogin = MagicMock()
        sociallogin.user = MagicMock()
        sociallogin.user.email = "hacker@other.com"
        with patch("bitcaster.social.adapter.config") as mock_config:
            mock_config.SOCIAL_AUTH_CREATE_USER = True
            mock_config.SOCIAL_AUTH_ACCEPTED_USERS = ".*@example.com, admin@bitcaster.io"
            assert adapter.is_open_for_signup(request_mock, sociallogin) is False

    def test_pre_social_login_forbidden_signup(self, adapter, request_mock):
        sociallogin = MagicMock(spec=SocialLogin)
        sociallogin.is_existing = False
        sociallogin.user = MagicMock()
        email_address = MagicMock()
        email_address.email = "hacker@other.com"
        sociallogin.email_addresses = [email_address]
        sociallogin.user.email = "hacker@other.com"

        with patch("bitcaster.social.adapter.config") as mock_config:
            mock_config.SOCIAL_AUTH_CREATE_USER = True
            mock_config.SOCIAL_AUTH_ACCEPTED_USERS = ".*@example.com"
            with pytest.raises(ImmediateHttpResponse):
                adapter.pre_social_login(request_mock, sociallogin)

    def test_pre_social_login_forbidden_signup_closed_registration(self, adapter, request_mock):
        sociallogin = MagicMock(spec=SocialLogin)
        sociallogin.is_existing = False
        sociallogin.user = MagicMock()
        email_address = MagicMock()
        email_address.email = "anyone@anywhere.com"
        sociallogin.email_addresses = [email_address]
        sociallogin.user.email = "anyone@anywhere.com"

        with patch("bitcaster.social.adapter.config") as mock_config:
            mock_config.SOCIAL_AUTH_CREATE_USER = False
            with pytest.raises(ImmediateHttpResponse) as exc:
                adapter.pre_social_login(request_mock, sociallogin)

            assert b"Registration is currently closed." in exc.value.response.content

    def test_pre_social_login_auto_connect(self, adapter, request_mock, existing_user):
        sociallogin = MagicMock(spec=SocialLogin)
        sociallogin.is_existing = False
        email_address = MagicMock()
        email_address.email = "test@example.com"
        sociallogin.email_addresses = [email_address]

        adapter.pre_social_login(request_mock, sociallogin)

        assert email_address.verified is True
        sociallogin.connect.assert_called_once_with(request_mock, existing_user)

    def test_pre_social_login_user_not_found(self, adapter, request_mock):
        sociallogin = MagicMock(spec=SocialLogin)
        sociallogin.is_existing = False
        sociallogin.user = MagicMock()
        email_address = MagicMock()
        email_address.email = "nonexistent@example.com"
        sociallogin.email_addresses = [email_address]
        sociallogin.user.email = "nonexistent@example.com"

        adapter.pre_social_login(request_mock, sociallogin)
        sociallogin.connect.assert_not_called()

    def test_populate_user(self, adapter, request_mock):
        sociallogin = MagicMock()
        data = {"email": "new@example.com"}

        populated_user = adapter.populate_user(request_mock, sociallogin, data)
        assert populated_user.email == "new@example.com"
        assert populated_user.username == "new@example.com"

    def test_save_user_new_user_setup(self, adapter, request_mock, db):
        from testutils.factories import UserFactory

        group_name = "SocialUsers"
        Group.objects.get_or_create(name=group_name)

        user = UserFactory.build(email="newuser@example.com")
        sociallogin = MagicMock()
        sociallogin.user = user
        sociallogin.account = MagicMock(spec=SocialAccount)

        def mock_save_user_side_effect(*args, **kwargs):
            user.save()
            return user

        with (
            patch(
                "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.save_user",
                side_effect=mock_save_user_side_effect,
            ),
            patch("bitcaster.social.adapter.config") as mock_config,
        ):
            mock_config.NEW_USER_DEFAULT_GROUP = group_name

            saved_user = adapter.save_user(request_mock, sociallogin)
            assert saved_user.pk is not None
            saved_user.refresh_from_db()

            assert saved_user.groups.filter(name=group_name).exists()
            from bitcaster.models import Address

            assert Address.objects.filter(user=saved_user, type=AddressType.EMAIL, value="newuser@example.com").exists()

    def test_save_user_group_not_found(self, adapter, request_mock, db):
        from testutils.factories import UserFactory

        user = UserFactory.build(email="newuser2@example.com")
        sociallogin = MagicMock()
        sociallogin.user = user
        sociallogin.account = MagicMock(spec=SocialAccount)

        def mock_save_user_side_effect(*args, **kwargs):
            user.save()
            return user

        with (
            patch(
                "allauth.socialaccount.adapter.DefaultSocialAccountAdapter.save_user",
                side_effect=mock_save_user_side_effect,
            ),
            patch("bitcaster.social.adapter.config") as mock_config,
        ):
            mock_config.NEW_USER_DEFAULT_GROUP = "NonExistentGroup"
            # Should not raise exception
            adapter.save_user(request_mock, sociallogin)

    def test_get_app_not_found(self, adapter, request_mock):
        with patch("allauth.socialaccount.adapter.DefaultSocialAccountAdapter.get_app") as mock_super:
            adapter.get_app(request_mock, "nonexistent")
            mock_super.assert_called_once()

    def test_get_app_with_client_id_disambiguates(self, adapter, request_mock, oidc_providers):
        app = adapter.get_app(request_mock, "openid_connect", client_id="first-client")
        assert app.client_id == "first-client"
        assert app.provider == "openid_connect"

    def test_get_allowed_emails_caching(self, adapter, request_mock):
        from django.core.cache import cache

        key = "bitcaster:social:allowed_emails"
        cache.delete(key)
        try:
            with patch("bitcaster.social.adapter.config") as mock_config:
                mock_config.SOCIAL_AUTH_ACCEPTED_USERS = "first@example.com, second@example.com"
                result = adapter.get_allowed_emails()
                assert len(result) == 2
            with patch("bitcaster.social.adapter.config") as mock_config:
                mock_config.SOCIAL_AUTH_ACCEPTED_USERS = "other@example.com"
                result = adapter.get_allowed_emails()
                assert len(result) == 2
        finally:
            cache.delete(key)

    def test_get_app_raises_on_ambiguous_provider(self, adapter, request_mock, oidc_providers):
        from bitcaster.social.models import SocialProvider

        with pytest.raises(SocialProvider.MultipleObjectsReturned):
            adapter.get_app(request_mock, "openid_connect")

    def test_get_app_with_numeric_provider(self, adapter, request_mock):
        from testutils.factories import SocialProviderFactory

        provider = SocialProviderFactory.create(provider="google", client_id="pk-client-id", secret="pk-secret")
        app = adapter.get_app(request_mock, str(provider.pk))
        assert app.client_id == "pk-client-id"
        assert app.provider == "google"


@pytest.mark.django_db
class TestBitcasterAccountAdapter:
    @pytest.fixture
    def adapter(self):
        return BitcasterAccountAdapter()

    @pytest.fixture
    def request_mock(self):
        return MagicMock()

    def test_is_open_for_signup(self, adapter, request_mock):
        with patch("bitcaster.social.adapter.config") as mock_config:
            mock_config.SOCIAL_AUTH_CREATE_USER = True
            assert adapter.is_open_for_signup(request_mock) is True

            mock_config.SOCIAL_AUTH_CREATE_USER = False
            assert adapter.is_open_for_signup(request_mock) is False
