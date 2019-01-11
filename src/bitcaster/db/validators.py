# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from ratelimit.utils import _split_rate

logger = logging.getLogger(__name__)

RESERVED_NAMES = frozenset((
    # operations
    'add', 'edit', 'remove', 'delete', 'del', 'update', 'accept', 'enroll'
    # names
                                                                  'bitcaster', 'sax', 'bitcaster',
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


@deconstructible
class ReservedWordValidator:
    message = _("'%(value)s' is a bitcaster reserved word")

    def __call__(self, value):
        if value.lower() in RESERVED_NAMES:
            raise ValidationError(self.message, params={'value': value})


check_reserved = ReservedWordValidator()


@deconstructible
class RateLimitValidator:
    message = _("'%(value)s'is not a valid ratelimit value ")

    def __call__(self, value):
        try:
            _split_rate(value)
        except Exception:
            raise ValidationError(self.message, params={'value': value})
