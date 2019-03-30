# -*- coding: utf-8 -*-
import logging

from django.utils.translation import gettext as _
from model_utils import Choices

logger = logging.getLogger(__name__)

ROLES = Choices(
    (1, 'OWNER', _('Owner')),
    (2, 'ADMIN', _('Admin')),
    (4, 'SUBSCRIBER', _('Subscriber')))

OPS = {'manage', 'access'}
TARGETS = {'application', 'organization'}


# ROLES = {'admin', 'subscriber'}


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
ADMIN_PERMISSIONS = build(['manage'])
SUBSCRIBER_PERMISSIONS = set()

PERM_MAP = {ROLES.OWNER: ADMIN_PERMISSIONS,
            ROLES.ADMIN: ADMIN_PERMISSIONS,
            ROLES.SUBSCRIBER: SUBSCRIBER_PERMISSIONS}
