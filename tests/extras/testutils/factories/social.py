from factory import fuzzy

from bitcaster.social.models import SocialProvider, Provider

from .base import AutoRegisterModelFactory


class SocialProviderFactory(AutoRegisterModelFactory):
    provider = fuzzy.FuzzyChoice(Provider)

    class Meta:
        model = SocialProvider
        django_get_or_create = ("provider",)
