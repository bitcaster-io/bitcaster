# -*- coding: utf-8 -*-
"""
mercury / validators
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)

RESERVED_NAMES = frozenset((
    # operations
    'add', 'edit', 'remove', 'delete', 'del', 'update', 'accept', 'enroll'
    # names
                                                                  'bitcaster', 'sax', 'mercury',
    # roles
    'admin', 'manage', 'account', 'register', 'api', 'superuser',
    # models
    'org', 'organization', 'organizations',
    'app', 'application', 'applications',
    'user', 'users',
    'team', 'teams',
    # urls
    'invite', 'details', 'members', 'channels', 'applications', 'send',
    'help',
    'main',
    'login', 'logout', '404', '500', '_static', 'out', 'debug',
    'remote', 'get-cli', 'blog', 'welcome', 'features',
    'customers', 'integrations', 'signup', 'pricing',
    'subscribe', 'enterprise', 'about', 'jobs', 'thanks', 'guide',
    'privacy', 'security', 'terms', 'from', 'sponsorship', 'for',
    'at', 'platforms', 'branding', 'vs', 'answers', '_admin',
    'support', 'register', 'profile',
    # generic forbidden words
    'email', 'mail'
))


class CoreName(str):
    pass


def mark_core(value):
    return CoreName(value)


class ReservedWordValidator:
    message = _("'{value}' is a bitcaster reserved word")

    def __call__(self, value):
        # if isinstance(value, CoreName):
        #     return
        if value.lower() in RESERVED_NAMES:
            raise ValidationError(self.message, params={"value": value})
