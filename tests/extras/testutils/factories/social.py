from factory import fuzzy

from bitcaster.social.models import Provider, SocialProvider

from .base import AutoRegisterModelFactory


class SocialProviderFactory(AutoRegisterModelFactory[SocialProvider]):
    provider = fuzzy.FuzzyChoice(Provider)

    class Meta:
        model = SocialProvider
        django_get_or_create = ("provider",)
