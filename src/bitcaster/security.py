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

PERMISSIONS = set()
for op in OPS:
    for target in TARGETS:
        PERMISSIONS.add('%s_%s' % (op, target))

PERMISSIONS.add('admin')

# PERM_MAP = {}
# for role in ROLES:
#     PERM_MAP[role] = PERMISSIONS

OWNER_PERMISSIONS = PERMISSIONS
ADMIN_PERMISSIONS = PERMISSIONS
SUBSCRIBER_PERMISSIONS = PERMISSIONS

PERM_MAP = {Role.ADMIN: ADMIN_PERMISSIONS,
            Role.OWNER: OWNER_PERMISSIONS,
            Role.SUBSCRIBER: SUBSCRIBER_PERMISSIONS}
