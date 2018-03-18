# -*- coding: utf-8 -*-
import logging

from django import forms
from django.forms import Form

logger = logging.getLogger(__name__)


class SettingsOAuthForm(Form):
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = forms.CharField(required=False)
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = forms.CharField(required=False)

    SOCIAL_AUTH_GITHUB_KEY = forms.CharField(required=False)
    SOCIAL_AUTH_GITHUB_SECRET = forms.CharField(required=False)

    SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = forms.CharField(required=False)
    SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = forms.CharField(required=False)


class SettingsChannelsForm(Form):
    pass


class SettingsMainForm(Form):
    SITE_URL = forms.CharField()
    RECAPTCHA_PUBLIC_KEY = forms.CharField(required=False)
    RECAPTCHA_PRIVATE_KEY = forms.CharField(required=False)
    SENTRY_DSN = forms.CharField(required=False)
    ENABLE_SENTRY = forms.BooleanField(required=False)


class SettingsEmailForm(Form):
    EMAIL_HOST = forms.CharField(required=False)
    EMAIL_HOST_PORT = forms.IntegerField(required=False)
    EMAIL_HOST_USER = forms.CharField(required=False)
    EMAIL_HOST_PASSWORD = forms.CharField(required=False)
    EMAIL_USE_TLS = forms.BooleanField(required=False)
    EMAIL_SENDER = forms.EmailField(required=False)
    EMAIL_SUBJECT_PREFIX = forms.CharField(required=False)
