# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from constance import config
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import Promise
from requests import HTTPError
from social_core.backends.github import GithubOAuth2
from social_django.strategy import DjangoStrategy

from bitcaster.db.fields import Role
from bitcaster.exceptions import NotMemberOfOrganization
from bitcaster.models import Organization, OrganizationMember, User

# from social_core.pipeline.user import create_user


# def associate(backend, details, user=None, *args, **kwargs):
#     return None


USER_FIELDS = ['username', 'email', 'fullname']


def associate_invitation(backend, details, user=None, strategy=None, *args, **kwargs):
    invitation_id = strategy.session_get('invitation')
    is_new = False
    if invitation_id:
        invite = OrganizationMember.objects.get(pk=invitation_id, user__isnull=True)
        # if not user:
        is_new = True
        fields = {'email': details['email'],
                  'name': details['fullname'],
                  'friendly_name': details['username']}
        user = User.objects.create(**fields)
        invite.user = user
        invite.date_enrolled = timezone.now()
        invite.save()

    return {
        'is_new': is_new,
        'user': user
    }


def create_default_membership(backend, details, new_association=False, uid=None, *args, **kwargs):
    if new_association:
        fields = {'email': details['email'],
                  'name': details['fullname'],
                  'friendly_name': details['username']}

        user, created = User.objects.get_or_create(email=details['email'], defaults=fields)
        if created:
            user.memberships.create(organization=Organization.objects.first(),
                                    role=Role.SUBSCRIBER)
            social = backend.strategy.storage.user.create_social_auth(
                user, uid, backend.name
            )
        else:
            social = kwargs['social']
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
        if name == 'SOCIAL_AUTH_GOOGLE_OAUTH2_WHITELISTED_DOMAINS':
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


class BitcasterGithubOrganizationOAuth2(GithubOAuth2):
    """Github OAuth2 authentication backend for organizations"""
    name = 'github-org'
    no_member_string = 'User doesn\'t belong to the organization'

    def member_url(self, user_data):
        return urljoin(
            self.api_url(),
            'orgs/{org}/members/{username}'.format(
                org=self.setting('NAME'),
                username=user_data.get('login')
            )
        )

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""
        user_data = super(BitcasterGithubOrganizationOAuth2, self).user_data(
            access_token, *args, **kwargs
        )
        try:
            self.request(self.member_url(user_data), params={
                'access_token': access_token
            })
        except HTTPError as err:
            # if the user is a member of the organization, response code
            # will be 204, see http://bit.ly/ZS6vFl
            if err.response.status_code != 204:
                raise NotMemberOfOrganization(self,
                                              'User doesn\'t belong to the organization')
        return user_data
