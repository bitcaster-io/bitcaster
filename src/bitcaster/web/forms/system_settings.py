# -*- coding: utf-8 -*-
import logging

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django import forms
from django.forms import Form

logger = logging.getLogger(__name__)


class SettingsForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


class SettingsOAuthForm(SettingsForm):
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = forms.CharField(label='Key', required=False)
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = forms.CharField(label='Secret', required=False)
    SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = forms.CharField(label='Allowed domains',
                                                                    help_text='comma separated list of allowed domains',
                                                                    required=False)

    SOCIAL_AUTH_GITHUB_ORG_NAME = forms.CharField(label='Organization name', required=False)
    SOCIAL_AUTH_GITHUB_ORG_KEY = forms.CharField(label='Key', required=False)
    SOCIAL_AUTH_GITHUB_ORG_SECRET = forms.CharField(label='Secret', required=False)

    SOCIAL_AUTH_GITHUB_KEY = forms.CharField(label='Key', required=False)
    SOCIAL_AUTH_GITHUB_SECRET = forms.CharField(label='Secret', required=False)

    # SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = forms.CharField(required=False)
    # SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = forms.CharField(required=False)\

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset('Google',
                     'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY',
                     'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET',
                     'SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS',
                     ),
            Fieldset('GitHub - ORg',
                     'SOCIAL_AUTH_GITHUB_ORG_NAME',
                     'SOCIAL_AUTH_GITHUB_ORG_KEY',
                     'SOCIAL_AUTH_GITHUB_ORG_SECRET',
                     ),
            Fieldset('GitHub',
                     'SOCIAL_AUTH_GITHUB_KEY',
                     'SOCIAL_AUTH_GITHUB_SECRET',
                     ),
            Submit('submit', 'Save')
        )


class SettingsChannelsForm(Form):
    pass


class SettingsMainForm(Form):
    SITE_URL = forms.CharField()
    # RECAPTCHA_PUBLIC_KEY = forms.CharField(required=False)
    # RECAPTCHA_PRIVATE_KEY = forms.CharField(required=False)


class SettingsEmailForm(Form):
    EMAIL_HOST = forms.CharField(required=True)
    EMAIL_HOST_PORT = forms.IntegerField(required=True)
    EMAIL_HOST_USER = forms.CharField(required=True)
    EMAIL_HOST_PASSWORD = forms.CharField(required=False)
    EMAIL_USE_TLS = forms.BooleanField(required=False)
    EMAIL_SENDER = forms.EmailField(required=True)
    EMAIL_SUBJECT_PREFIX = forms.CharField(required=False)
