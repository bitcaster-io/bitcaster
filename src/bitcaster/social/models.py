from typing import List, Tuple

from django.db import models
from django.utils.translation import gettext as _


class Provider(models.TextChoices):
    AZUREAD_OAUTH2 = "AZUREAD_OAUTH2", "Azure"
    AZUREAD_TENANT_OAUTH2 = "AZUREAD_TENANT_OAUTH2", "Azure Tenant"
    FACEBOOK = "FACEBOOK", "Facebook"
    GITHUB = "GITHUB", "Github"
    GITHUB_ENTERPRISE = "GITHUB_ENTERPRISE", "Github Enterprise"
    GITHUB_ORG = "GITHUB_ORG", "Github Organization"
    GITLAB = "GITLAB", "Gitlab"
    GITHUB_TEAM = "GITHUB_TEAM", "Github Team"
    GOOGLE_OAUTH2 = "GOOGLE_OAUTH2", "Google"
    LINKEDIN_OAUTH2 = "LINKEDIN_OAUTH2", "Linkedin"
    TWITTER = "TWITTER", "Twitter"


class SocialProviderManager(models.Manager["SocialProvider"]):
    def choices(self) -> List[Tuple[str, str]]:
        ret = []
        for obj in self.filter(enabled=True):
            ret.append((obj.code, obj.label))
        return ret


class SocialProvider(models.Model):
    provider = models.CharField(
        max_length=30,
        help_text=_("Social Login provider"),
        choices=Provider.choices,
        unique=True,
    )
    configuration = models.JSONField(default=dict, blank=True, help_text=_("Configuration as per Python Social Auth"))
    enabled = models.BooleanField(default=True)
    objects = SocialProviderManager()

    class Meta:
        app_label = "social"

    @property
    def code(self) -> str:
        return self.provider.lower().replace("_", "-")

    @property
    def label(self) -> str:
        return Provider[self.provider.replace("-", "_")].label

    def __str__(self) -> str:
        return self.provider
