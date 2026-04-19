from django.db import models
from django.utils.translation import gettext_lazy as _


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
    OAUTH2 = "OAUTH2", "oauth2"
    WSO2 = "WSO2", "Wso2"
    KEYCLOAK = "KEYCLOAK", "Keycloak"


class SocialProviderManager(models.Manager["SocialProvider"]):
    def choices(self) -> list[tuple[str, str]]:
        return [(obj.code, obj.label) for obj in self.filter(enabled=True)]


class SocialProvider(models.Model):
    label = models.CharField(verbose_name=_("label"), max_length=50, unique=True, help_text=_("Label"))
    provider = models.CharField(
        verbose_name=_("provider"),
        max_length=30,
        choices=Provider.choices,
        unique=True,
        help_text=_("Social Login provider"),
    )
    configuration = models.JSONField(
        verbose_name=_("Configuration"),
        blank=True,
        default=dict,
        help_text=_("Configuration as per Python Social Auth"),
    )
    enabled = models.BooleanField(verbose_name=_("Enabled"), default=True, help_text=_("Provider status"))
    objects = SocialProviderManager()

    class Meta:
        app_label = "social"

    def __str__(self) -> str:
        return self.provider

    @property
    def code(self) -> str:
        return self.provider.lower().replace("_", "-")
