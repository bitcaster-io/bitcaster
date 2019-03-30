# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from constance import config
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import resolve_url
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import Promise
from requests import HTTPError
from sentry_sdk import capture_exception
from social_core.backends.github import GithubOAuth2
from social_django.strategy import DjangoStrategy

from bitcaster.exceptions import NotMemberOfOrganization
from bitcaster.models import Invitation, Organization, User
from bitcaster.security import ROLES

USER_FIELDS = ['username', 'email', 'fullname']


def associate_invitation(backend, details, user=None, strategy=None, *args, **kwargs):
    invitation_id = strategy.session_get('invitation')
    is_new = kwargs['is_new']
    if is_new:
        fields = {'email': details['email'],
                  'name': details['fullname'],
                  'friendly_name': details['username']}
        if invitation_id:
            invite = Invitation.objects.get(pk=id, date_accepted__isnull=True)
            invite.date_accepted = timezone.now()
            invite.save()
            organization = invite.organization
            # application = invite.application
            role = invite.role

            if invite:
                is_new = True
        else:
            organization = Organization.objects.get()
            role = ROLES.SUBSCRIBER

        user = User.objects.create(**fields)
        organization.memberships.create(user=user, role=role)

    return {
        'is_new': is_new,
        'user': user
    }


def create_default_membership(backend, details, new_association=False, uid=None, *args, **kwargs):
    # this must be called AFTER associate_invitation
    # invitation_id = backend.strategy.session_get('invitation')
    # if invitation_id:
    #     invite = OrganizationMember.objects.filter(pk=invitation_id, user__isnull=False).first()

    if new_association:
        storage = backend.strategy.storage
        user = User.objects.get(email=details['email'])
        try:
            social = storage.user.create_social_auth(user, uid, backend.name)
        except IntegrityError:
            capture_exception()
            social = storage.user.get_social_auth(backend.name, uid)
        except Exception:
            capture_exception()
            raise

        return {'user': user,
                'is_new': user is None,
                'new_association': social is None,
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
            capture_exception()
            # if the user is a member of the organization, response code
            # will be 204, see http://bit.ly/ZS6vFl
            if err.response.status_code != 204:
                raise NotMemberOfOrganization(self, user_data)
        except Exception:
            capture_exception()
            raise
        return user_data
