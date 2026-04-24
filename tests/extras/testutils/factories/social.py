import factory
from factory import fuzzy

from bitcaster.social.models import Provider, SocialProvider

from .base import AutoRegisterModelFactory


class SocialProviderFactory(AutoRegisterModelFactory[SocialProvider]):
    provider = fuzzy.FuzzyChoice(Provider)
    label = factory.LazyAttribute(lambda o: o.provider.label.title())

    class Meta:
        model = SocialProvider
        django_get_or_create = ("provider",)
