from django import forms
from django.db import models


class Provider(models.TextChoices):
    GITHUB = "GITHUB", "Github"
    GOOGLE = "GOOGLE", "Google"


class GoogleConfig(forms.Form):
    pass


class SocialProvider(models.Model):
    provider = models.CharField(max_length=30, choices=Provider.choices)
    credentials = models.JSONField(default={}, blank=True)
