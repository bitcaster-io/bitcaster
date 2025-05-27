from django.shortcuts import resolve_url
from social_django.strategy import DjangoStrategy

from bitcaster.social.models import Provider, SocialProvider

caches = {}


class BitcasterStrategy(DjangoStrategy):
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
