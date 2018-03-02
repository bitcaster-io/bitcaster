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


def associate(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same email address in the DB.

    This pipeline entry is not 100% secure unless you know that the providers
    enabled enforce email verification on their side, otherwise a user can
    attempt to take over another user account by using the same (not validated)
    email address on some provider.  This pipeline entry is disabled by
    default.
    """
    return None


def avatar(backend, details, user=None, *args, **kwargs):
    # user.is_new = True
    is_new = kwargs.get('is_new', False)
    print(111, details)
    print(111, user)
    print(111, backend)
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
