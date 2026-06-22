from typing import Any, cast

import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp, SocialLogin
from constance import config

from django.contrib.auth.models import Group
from django.core.cache import cache
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.translation import gettext as _
from django_regex.utils import RegexList

from bitcaster.constants import AddressType
from bitcaster.models import Address, User
from bitcaster.social.models import SocialProvider

logger = logging.getLogger(__name__)


class BitcasterAccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return cast("bool", config.SOCIAL_AUTH_CREATE_USER)


class BitcasterSocialAccountAdapter(DefaultSocialAccountAdapter):
    def _build_social_app(self, db_provider: SocialProvider) -> SocialApp:
        cid = db_provider.client_id or db_provider.configuration.get("client_id")
        secret = db_provider.secret or db_provider.configuration.get("secret")
        key = db_provider.key or db_provider.configuration.get("key", "")

        return SocialApp(
            provider=db_provider.provider,
            provider_id=str(db_provider.pk),
            name=db_provider.label,
            client_id=cid,
            secret=secret,
            settings=db_provider.configuration,
            key=key,
        )

    def get_app(self, request: HttpRequest, provider: str | int, client_id: str | None = None) -> SocialApp:
        if (
            db_provider := SocialProvider.objects.filter(pk=provider, enabled=True).first()
            if isinstance(provider, int) or provider.isdigit()
            else SocialProvider.objects.filter(provider=provider, enabled=True).first()
        ):
            return self._build_social_app(db_provider)
        return None

    def is_open_for_signup(self, request: HttpRequest, sociallogin: SocialLogin) -> bool:
        if not config.SOCIAL_AUTH_CREATE_USER:
            return False

        email = cast("str", sociallogin.user.email)
        if config.SOCIAL_AUTH_ACCEPTED_USERS:
            return email in self.get_allowed_emails()
        return True

    def is_auto_signup_allowed(self, request: HttpRequest, sociallogin: SocialLogin) -> bool:
        return cast("bool", config.SOCIAL_AUTH_CREATE_USER)

    def get_allowed_emails(self) -> RegexList:
        key = "bitcaster:social:allowed_emails"
        allowed = cache.get(key)
        if allowed is None:
            allowed = RegexList(cast("str", config.SOCIAL_AUTH_ACCEPTED_USERS).split(","))
            cache.set(key, allowed, 300)
        return cast("RegexList", allowed)

    def pre_social_login(self, request: HttpRequest, sociallogin: SocialLogin) -> None:
        # Force email to be verified to allow auto-connect and auto-signup
        for email_address in sociallogin.email_addresses:
            email_address.verified = True

        if not sociallogin.is_existing:
            email = None
            if sociallogin.email_addresses:
                email = sociallogin.email_addresses[0].email

            if email:
                try:
                    user = User.objects.get(email=email)
                    sociallogin.connect(request, user)
                except User.DoesNotExist:
                    # check if signup is allowed
                    if not self.is_open_for_signup(request, sociallogin):
                        if not config.SOCIAL_AUTH_CREATE_USER:
                            msg = _("Registration is currently closed.")
                        else:
                            msg = _("Your email address (%s) is not allowed to register.") % email

                        response = render(
                            request,
                            "bitcaster/social/registration_error.html",
                            {"error_message": msg},
                        )
                        raise ImmediateHttpResponse(response) from None

        super().pre_social_login(request, sociallogin)

    def populate_user(self, request: HttpRequest, sociallogin: SocialLogin, data: dict[str, Any]) -> User:
        user = cast("User", super().populate_user(request, sociallogin, data))
        email = data.get("email") or sociallogin.account.extra_data.get("email")
        if email:
            user.email = email
            user.username = email
        return user

    def save_user(self, request: HttpRequest, sociallogin: SocialLogin, form: Any = None) -> User:
        user = sociallogin.user
        is_new = user.pk is None
        user = cast("User", super().save_user(request, sociallogin, form))
        if is_new:
            try:
                grp = Group.objects.get(name=config.NEW_USER_DEFAULT_GROUP)
                user.groups.add(grp)
            except Group.DoesNotExist:
                pass

            Address.objects.get_or_create(user=user, name="email", type=AddressType.EMAIL, value=user.email)
        return user
