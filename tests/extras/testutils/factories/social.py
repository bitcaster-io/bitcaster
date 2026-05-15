import factory
from factory import fuzzy

from bitcaster.social.models import SocialProvider

from .base import AutoRegisterModelFactory

PROVIDER_LABELS = {
    "facebook": "Facebook",
    "github": "Github",
    "gitlab": "Gitlab",
    "google": "Google",
    "linkedin_oauth2": "Linkedin",
    "microsoft": "Microsoft",
    "twitter": "Twitter",
    "wso2": "Wso2",
    "openid_connect": "Keycloak",
}


class SocialProviderFactory(AutoRegisterModelFactory[SocialProvider]):
    provider = fuzzy.FuzzyChoice(list(PROVIDER_LABELS.keys()))
    label = factory.LazyAttribute(lambda o: PROVIDER_LABELS.get(o.provider, o.provider))
    slug = factory.Sequence(lambda n: f"provider-{n}")

    class Meta:
        model = SocialProvider
        django_get_or_create = ("provider",)
