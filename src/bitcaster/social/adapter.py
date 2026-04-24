import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp
from constance import config
from django.contrib.auth.models import Group

from bitcaster.constants import AddressType
from bitcaster.models import Address, User
from bitcaster.social.models import SocialProvider

logger = logging.getLogger(__name__)


class BitcasterAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return config.SOCIAL_AUTH_CREATE_USER


class BitcasterSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_app(self, request, provider, client_id=None):
        try:
            db_provider = SocialProvider.objects.get(provider=provider, enabled=True)

            # Read from dedicated fields first, fallback to JSON
            cid = db_provider.client_id or db_provider.configuration.get("client_id")
            secret = db_provider.secret or db_provider.configuration.get("secret")
            key = db_provider.key or db_provider.configuration.get("key", "")

            # Legacy compatibility lookups (if still empty)
            if not cid or not secret:
                legacy_map = {
                    "google": "GOOGLE_OAUTH2",
                    "microsoft": "AZUREAD_OAUTH2",
                    "facebook": "FACEBOOK",
                    "github": "GITHUB",
                    "gitlab": "GITLAB",
                    "linkedin_oauth2": "LINKEDIN_OAUTH2",
                    "twitter": "TWITTER",
                    "openid_connect": "KEYCLOAK",
                    "wso2": "OAUTH2",
                }
                suffix = legacy_map.get(provider, provider.upper())
                cid = cid or db_provider.configuration.get(f"SOCIAL_AUTH_{suffix}_KEY")
                secret = secret or db_provider.configuration.get(f"SOCIAL_AUTH_{suffix}_SECRET")

            return SocialApp(
                provider=provider,
                name=db_provider.label,
                client_id=cid,
                secret=secret,
                key=key,
            )
        except SocialProvider.DoesNotExist:
            return super().get_app(request, provider, client_id)

    def is_auto_signup_allowed(self, request, sociallogin):
        return True

    def pre_social_login(self, request, sociallogin):
        # Force email to be verified to allow auto-connect and auto-signup
        for email in sociallogin.email_addresses:
            email.verified = True

        if not sociallogin.is_existing:
            email = None
            if sociallogin.email_addresses:
                email = sociallogin.email_addresses[0].email

            if email:
                try:
                    user = User.objects.get(email=email)
                    sociallogin.connect(request, user)
                except User.DoesNotExist:
                    pass

        return super().pre_social_login(request, sociallogin)

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        email = data.get("email") or sociallogin.account.extra_data.get("email")
        if email:
            user.email = email
            user.username = email
        return user

    def save_user(self, request, sociallogin, form=None):
        user = sociallogin.user
        is_new = user.pk is None
        user = super().save_user(request, sociallogin, form)
        if is_new:
            try:
                grp = Group.objects.get(name=config.NEW_USER_DEFAULT_GROUP)
                user.groups.add(grp)
            except Group.DoesNotExist:
                pass

            Address.objects.get_or_create(user=user, name="email", type=AddressType.EMAIL, value=user.email)
        return user
