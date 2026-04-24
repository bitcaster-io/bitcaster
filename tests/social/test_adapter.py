from unittest.mock import MagicMock, patch

import pytest
from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.contrib.auth.models import Group

from bitcaster.constants import AddressType
from bitcaster.models import Address, User
from bitcaster.social.adapter import BitcasterAccountAdapter, BitcasterSocialAccountAdapter
from bitcaster.social.models import SocialProvider


@pytest.mark.django_db
class TestBitcasterSocialAccountAdapter:
    @pytest.fixture
    def adapter(self):
        return BitcasterSocialAccountAdapter()

    @pytest.fixture
    def request_mock(self):
        return MagicMock()

    def test_get_app_from_dedicated_fields(self, adapter, request_mock):
        SocialProvider.objects.create(
            provider="google", label="Google", client_id="test-client-id", secret="test-secret"
        )
        app = adapter.get_app(request_mock, "google")
        assert app.client_id == "test-client-id"
        assert app.secret == "test-secret"
        assert app.provider == "google"

    def test_get_app_legacy_compatibility(self, adapter, request_mock):
        # Test fallback to SOCIAL_AUTH_<PROVIDER>_KEY format in JSON configuration
        SocialProvider.objects.create(
            provider="google",
            label="Google",
            configuration={
                "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY": "legacy-id",
                "SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET": "legacy-secret",
            },
        )
        app = adapter.get_app(request_mock, "google")
        assert app.client_id == "legacy-id"
        assert app.secret == "legacy-secret"

    def test_is_auto_signup_allowed(self, adapter, request_mock):
        assert adapter.is_auto_signup_allowed(request_mock, MagicMock()) is True

    def test_pre_social_login_auto_connect(self, adapter, request_mock):
        user = User.objects.create(email="test@example.com", username="test@example.com")

        sociallogin = MagicMock(spec=SocialLogin)
        sociallogin.is_existing = False
        email_address = MagicMock()
        email_address.email = "test@example.com"
        sociallogin.email_addresses = [email_address]

        adapter.pre_social_login(request_mock, sociallogin)

        assert email_address.verified is True
        sociallogin.connect.assert_called_once_with(request_mock, user)

    def test_pre_social_login_user_not_found(self, adapter, request_mock):
        # Line 75 coverage: User.DoesNotExist
        sociallogin = MagicMock(spec=SocialLogin)
        sociallogin.is_existing = False
        email_address = MagicMock()
        email_address.email = "nonexistent@example.com"
        sociallogin.email_addresses = [email_address]

        # Should not raise exception
        adapter.pre_social_login(request_mock, sociallogin)
        sociallogin.connect.assert_not_called()

    def test_populate_user(self, adapter, request_mock):
        sociallogin = MagicMock()
        data = {"email": "new@example.com"}

        populated_user = adapter.populate_user(request_mock, sociallogin, data)
        assert populated_user.email == "new@example.com"
        assert populated_user.username == "new@example.com"

    def test_save_user_new_user_setup(self, adapter, request_mock, db):
        group_name = "SocialUsers"
        Group.objects.get_or_create(name=group_name)

        user = User(email="newuser@example.com", username="newuser@example.com")
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
            assert Address.objects.filter(user=saved_user, type=AddressType.EMAIL, value="newuser@example.com").exists()

    def test_save_user_group_not_found(self, adapter, request_mock, db):
        # Line 96 coverage: Group.DoesNotExist
        user = User(email="newuser2@example.com", username="newuser2@example.com")
        sociallogin = MagicMock()
        sociallogin.user = user
        sociallogin.account = MagicMock(spec=SocialAccount)

        # Ensure user is saved before being passed to filters
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


@pytest.mark.django_db
class TestBitcasterAccountAdapter:
    @pytest.fixture
    def adapter(self):
        return BitcasterAccountAdapter()

    @pytest.fixture
    def request_mock(self):
        return MagicMock()

    def test_is_open_for_signup(self, adapter, request_mock):
        # Line 18 coverage
        with patch("bitcaster.social.adapter.config") as mock_config:
            mock_config.SOCIAL_AUTH_CREATE_USER = True
            assert adapter.is_open_for_signup(request_mock) is True

            mock_config.SOCIAL_AUTH_CREATE_USER = False
            assert adapter.is_open_for_signup(request_mock) is False
