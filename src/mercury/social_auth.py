# -*- coding: utf-8 -*-
"""
mercury / social_auth
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""
from constance import config
from django.conf import settings
from django.shortcuts import resolve_url
from django.utils.encoding import force_text
from django.utils.functional import Promise
from social_django.strategy import DjangoStrategy

from mercury.models import OrganizationMember


def associate(backend, details, user=None, *args, **kwargs):
    return None


def associate_invitation(backend, details, user=None, *args, **kwargs):
    strategy = kwargs['strategy']
    invitation_id = strategy.session_get('invitation')
    if invitation_id:
        OrganizationMember.objects.filter(pk=invitation_id).update(user=user)
    return None


def avatar(backend, details, user=None, *args, **kwargs):
    # user.is_new = True
    is_new = kwargs.get('is_new', False)
    if is_new:
        pass

    return False


class MercuryStrategy(DjangoStrategy):
    def get_setting(self, name):
        value = getattr(config, name, None)
        if value is None:
            value = getattr(settings, name)
        # Force text on URL named settings that are instance of Promise
        if name.endswith('_URL'):
            if isinstance(value, Promise):
                value = force_text(value)
            value = resolve_url(value)
        return value
