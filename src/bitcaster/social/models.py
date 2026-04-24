from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from django.utils.functional import _StrPromise


class Provider(models.TextChoices):
    GITHUB = "github", "Github"
    GITLAB = "gitlab", "Gitlab"
    GOOGLE = "google", "Google"
    LINKEDIN = "linkedin_oauth2", "Linkedin"
    MICROSOFT = "microsoft", "Microsoft"
    TWITTER = "twitter", "Twitter"
    KEYCLOAK = "openid_connect", "Keycloak"


def get_provider_choices() -> "list[tuple[str, _StrPromise]]":
    return Provider.choices


class SocialProviderManager(models.Manager["SocialProvider"]):
    def as_choices(self) -> list[tuple[str, str]]:
        return [(obj.provider, obj.label) for obj in self.filter(enabled=True)]


class SocialProvider(models.Model):
    label = models.CharField(verbose_name=_("label"), max_length=50, unique=True, help_text=_("Label"))
    provider = models.CharField(
        verbose_name=_("provider"),
        max_length=30,
        choices=get_provider_choices,
        unique=True,
        help_text=_("Social Login provider"),
    )
    client_id = models.CharField(
        verbose_name=_("Client ID"), max_length=191, blank=True, help_text=_("App ID or Client ID")
    )
    secret = models.CharField(
        verbose_name=_("Secret"), max_length=191, blank=True, help_text=_("API Secret or Client Secret")
    )
    key = models.CharField(
        verbose_name=_("Key"), max_length=191, blank=True, help_text=_("Optional extra key (if required by provider)")
    )
    configuration = models.JSONField(
        verbose_name=_("Extra Configuration"),
        blank=True,
        default=dict,
        help_text=_("Extra provider-specific settings"),
    )
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=True, help_text=_("Provider status"))
    objects = SocialProviderManager()

    class Meta:
        app_label = "social"

    def __str__(self) -> str:
        return self.label

    @property
    def code(self) -> str:
        return self.provider
