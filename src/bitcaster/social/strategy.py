from constance import config
from django.shortcuts import resolve_url
from django_regex.utils import RegexList
from social_core.exceptions import AuthForbidden
from social_django.strategy import DjangoStrategy

from bitcaster.social.models import Provider, SocialProvider

caches = {}


class BitcasterStrategy(DjangoStrategy):
    def create_user(self, *args, **kwargs):
        email = kwargs.get("email")
        if config.SOCIAL_AUTH_ACCEPTED_USERS and email not in RegexList(config.SOCIAL_AUTH_ACCEPTED_USERS.split(",")):
            raise AuthForbidden(None)
        return super().create_user(*args, **kwargs)

    def get_setting(self, name: str) -> str | None:
        found = None
        configuration = None
        for provider in Provider.values:
            if name.startswith(f"SOCIAL_AUTH_{provider.upper()}"):
                found = provider
        if found in caches:
            configuration = caches[found]
        elif found:
            config_record = SocialProvider.objects.filter(provider=found).first()
            if config_record:
                configuration = config_record.configuration
                caches[found] = configuration
            else:
                raise ValueError(f"Provider {found} not found")
        if configuration:
            value = configuration[name]
            if name.endswith("_URL"):
                value = resolve_url(value)
            return value
        return super().get_setting(name)
