from constance import config
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django.utils.translation import gettext as _
from sentry_sdk import capture_exception
from social_core.backends.github import GithubOrganizationOAuth2
from social_core.backends.linkedin import LinkedinOAuth2
from social_core.exceptions import AuthFailed
from social_django.strategy import DjangoStrategy

from bitcaster.models import Invitation, Organization
from bitcaster.security import ORG_ROLES

USER_FIELDS = ['username', 'email', 'fullname']


def associate_invitation(backend, details, user=None, strategy=None, **kwargs):
    invitation_id = strategy.session_get('invitation')
    is_new = kwargs['is_new']
    organization = None,
    role = None
    if invitation_id:
        fields = {'name': details['fullname'],
                  'friendly_name': details['fullname']}
        if invitation_id:
            # user, is_new = User.objects.get_or_create(email=details['email'],
            #                                           defaults=fields)
            try:
                invite = Invitation.objects.get(pk=invitation_id, date_accepted__isnull=True)
            except Invitation.DoesNotExist:
                raise AuthFailed(backend, _('Invitation not found'))
            invite.date_accepted = timezone.now()
            invite.user = user
            invite.save()
            organization = invite.organization

            if invite.role == ORG_ROLES.SUPERUSER:
                fields['is_superuser'] = True
                role = ORG_ROLES.OWNER
            else:
                role = invite.role
    else:
        organization = Organization.objects.get()
        role = ORG_ROLES.MEMBER

    organization.memberships.get_or_create(user=user, role=role)

    return {
        'organization': organization,
        'role': role,
        'is_new': is_new,
        'user': user
    }


def link_social_account(backend, new_association=False, social=None, uid=None, user=None, **kwargs):
    if (new_association and user) and not social:
        storage = backend.strategy.storage
        try:
            social = storage.user.create_social_auth(user, uid, backend.name)
        except Exception:
            capture_exception()
            raise

        return {'user': user,
                'social': social}
    return {}


class BitcasterStrategy(DjangoStrategy):

    def redirect(self, url):
        return super().redirect(url or '/')

    def get_setting(self, name):
        notfound = object()
        "get configuration from 'constance.config' first "
        value = getattr(config, name, notfound)
        if name.endswith('_WHITELISTED_DOMAINS'):
            if value:
                return value.split(',')
            else:
                return []

        if value is notfound:
            value = getattr(settings, name)
        # Force text on URL named settings that are instance of Promise
        if name.endswith('_URL'):
            if isinstance(value, Promise):
                value = force_text(value)
            value = resolve_url(value)
        return value


class BitcasterLinkedinOAuth2(LinkedinOAuth2):
    pass


class BitcasterGithubOrganizationOAuth2(GithubOrganizationOAuth2):
    """Github OAuth2 authentication backend for organizations"""
    name = 'github-org'

    def auth_allowed(self, response, details):
        return super().auth_allowed(response, details)

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        try:
            user_data = super().user_data(access_token, *args, **kwargs)
            if not user_data.get('email'):
                raise AuthFailed(self, _('You must have a public email configured in GitHub. '
                                         'Goto Settings/Profile and choose your public email'))
        except AuthFailed:
            raise AuthFailed(self, _('Sorry, you do not seem to be a public member of %s') % self.setting('NAME'))

        return user_data
