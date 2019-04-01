# -*- coding: utf-8 -*-
import logging
import os

from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Fieldset, Layout, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.forms import Form
from rest_framework.reverse import reverse

from bitcaster.framework.forms.widgets import PasswordEyeInput
from bitcaster.state import state
from bitcaster.utils.constance import FieldMappingField, LdapDNField

logger = logging.getLogger(__name__)


class SettingsForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()


HELP = '''
<div class="oauth-help">
<div class="line1">Follow instruction at <a href="{help_url}">{help_label}</a></div>
<div class="line2">Set callback url to <div class="cb">{callback}</div></div>
</div>
'''


# .format("https://developers.google.com/+/web/signin/",
# reverse_lazy("social:complete", args=['google-oauth2'])
# "http://localhost:8000/complete/google-oauth2/"
# )


class SettingsLdapForm(SettingsForm):
    AUTH_LDAP_ENABLE = forms.BooleanField(label='Enable', required=False)
    AUTH_LDAP_SERVER_URI = forms.CharField(label='Server address', required=False)
    AUTH_LDAP_BIND_DN = forms.CharField(label='Bind DN', required=False)
    AUTH_LDAP_BIND_PASSWORD = forms.CharField(label='Bind Password', required=False)
    AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = forms.BooleanField(label='Bind as authenticating user',
                                                               required=False)

    AUTH_LDAP_START_TLS = forms.BooleanField(label='Use Tls', required=False)
    AUTH_LDAP_USER_ATTR_MAP = FieldMappingField(label='Field mapping', required=False)
    AUTH_LDAP_USER_DN_TEMPLATE = LdapDNField(label='User DN template', required=False)
    AUTH_LDAP_USER_QUERY_FIELD = forms.CharField(
        label="User field used for matching. Must be present in 'Field mapping'", required=False)

    AUTH_LDAP_ALWAYS_UPDATE_USER = forms.BooleanField(label='Always update user', required=False)
    # AUTH_LDAP_AUTHORIZE_ALL_USERS = forms.BooleanField(label='Authorize all users', required=False)
    # AUTH_LDAP_USER_SEARCH = forms.BooleanField(label='User search',
    #                                            required=False)


class SettingsOAuthForm(SettingsForm):
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = forms.CharField(label='Key', required=False)
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = forms.CharField(label='Secret', required=False)
    SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS = forms.CharField(label='Allowed domains',
                                                                    help_text='comma separated list of allowed domains',
                                                                    required=False)

    SOCIAL_AUTH_GITHUB_ORG_NAME = forms.CharField(label='Organization name', required=False)
    SOCIAL_AUTH_GITHUB_ORG_KEY = forms.CharField(label='Key', required=False)
    SOCIAL_AUTH_GITHUB_ORG_SECRET = forms.CharField(label='Secret', required=False)

    # SOCIAL_AUTH_GITHUB_KEY = forms.CharField(label='Key', required=False)
    # SOCIAL_AUTH_GITHUB_SECRET = forms.CharField(label='Secret', required=False)
    #
    # SOCIAL_AUTH_LINKEDIN_OAUTH2_KEY = forms.CharField(required=False)
    # SOCIAL_AUTH_LINKEDIN_OAUTH2_SECRET = forms.CharField(required=False)\

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper.layout = Layout(
            Fieldset('Google',
                     HTML(HELP.format(help_url='https://developers.google.com/+/web/signin/',
                                      help_label='https://developers.google.com/+/web/signin/',
                                      callback=reverse('social:complete',
                                                       args=['google-oauth2'],
                                                       request=state.request))),
                     'SOCIAL_AUTH_GOOGLE_OAUTH2_KEY',
                     'SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET',
                     'SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS',
                     ),

            Fieldset('GitHub - Organization',
                     HTML(HELP.format(
                         help_url='https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/',
                         help_label='https://developer.github.com/apps/building-oauth-apps/authorizing-oauth-apps/',
                         callback=reverse('social:complete',
                                          args=['github-org'],
                                          request=state.request))),
                     'SOCIAL_AUTH_GITHUB_ORG_NAME',
                     'SOCIAL_AUTH_GITHUB_ORG_KEY',
                     'SOCIAL_AUTH_GITHUB_ORG_SECRET',
                     ),
            # Fieldset('GitHub',
            #          'SOCIAL_AUTH_GITHUB_KEY',
            #          'SOCIAL_AUTH_GITHUB_SECRET',
            #          ),
            Submit('submit', 'Save')
        )


class SettingsChannelsForm(Form):
    pass


class SettingsMainForm(Form):
    SITE_URL = forms.URLField()
    ALLOW_CHANGE_PRIMARY_ADDRESS = forms.BooleanField(required=False)
    GOOGLE_ANALYTICS_CODE = forms.CharField(required=False)
    BACKUPS_LOCATION = forms.CharField(required=False)

    # RECAPTCHA_PRIVATE_KEY = forms.CharField(required=False)

    def clean_BACKUPS_LOCATION(self):
        value = self.cleaned_data['BACKUPS_LOCATION']
        if not os.path.isdir(value):
            raise ValidationError('"%s" is not a valid location' % value)
        return value


class SettingsEmailForm(Form):
    EMAIL_HOST = forms.CharField(required=True)
    EMAIL_HOST_PORT = forms.IntegerField(required=True)
    EMAIL_HOST_USER = forms.CharField(required=True)
    EMAIL_HOST_PASSWORD = forms.CharField(required=False, widget=PasswordEyeInput)
    EMAIL_USE_TLS = forms.BooleanField(required=False)
    EMAIL_SENDER = forms.EmailField(required=True)
    EMAIL_SUBJECT_PREFIX = forms.CharField(required=False)
