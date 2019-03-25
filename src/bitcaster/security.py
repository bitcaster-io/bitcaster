# -*- coding: utf-8 -*-
import logging

from django.utils.translation import gettext as _

from bitcaster.utils.enumfield import EnumField

logger = logging.getLogger(__name__)


class Role(EnumField):
    OWNER = 1
    ADMIN = 2
    SUBSCRIBER = 4

    @classmethod
    def as_choices(cls):
        return tuple(sorted([(int(cls.OWNER), _('Owner')),
                             (int(cls.ADMIN), _('Admin')),
                             (int(cls.SUBSCRIBER), _('Subscriber'))]))


OPS = {'add', 'manage', 'delete'}
TARGETS = {'channel', 'monitor', 'subscription', 'event', 'application', 'organization'}
ROLES = {'owner', 'admin', 'subscriber'}


def build(ops):
    ret = set()
    for op in ops:
        for target in TARGETS:
            ret.add('%s_%s' % (op, target))
    return ret


# PERMISSIONS.add('admin')

# PERM_MAP = {}
# for role in ROLES:
#     PERM_MAP[role] = PERMISSIONS

ALL_PERMISSIONS = build(OPS)
ALL_PERMISSIONS.add('admin')

OWNER_PERMISSIONS = build(OPS)
OWNER_PERMISSIONS.add('admin')
ADMIN_PERMISSIONS = build(['manage'])
SUBSCRIBER_PERMISSIONS = set()

PERM_MAP = {Role.ADMIN: ADMIN_PERMISSIONS,
            Role.OWNER: OWNER_PERMISSIONS,
            Role.SUBSCRIBER: SUBSCRIBER_PERMISSIONS}
