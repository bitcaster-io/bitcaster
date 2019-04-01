# -*- coding: utf-8 -*-
import logging

from django.utils.translation import gettext as _
from model_utils import Choices

logger = logging.getLogger(__name__)

ROLES = Choices(
    (99, 'SUPERUSER', _('Superuser')),  # Access to system settings
    (1, 'OWNER', _('Owner')),  # Organization Owner
    (2, 'ADMIN', _('Admin')),  # Application Admin
    (4, 'MEMBER', _('Member')))


APP_ROLES = Choices(
    (ROLES.ADMIN, 'ADMIN', _('Admin')),  # Application Admin
    (ROLES.MEMBER, 'MEMBER', _('Member'))
)

ALL_PERMISSIONS = set()
OWNER_PERMISSIONS = {'manage_organization',
                     'create_channel',
                     'edit_channel',
                     'create_application',
                     'manage_application',
                     'invite_member', # invite new Organization member from within an app
                     }
ADMIN_PERMISSIONS = set()
MEMBER_PERMISSIONS = set()
ALL_PERMISSIONS.update(OWNER_PERMISSIONS)
ALL_PERMISSIONS.update(ADMIN_PERMISSIONS)
ALL_PERMISSIONS.update(MEMBER_PERMISSIONS)
ALL_PERMISSIONS.add('admin_system')

PERM_MAP = {ROLES.OWNER: OWNER_PERMISSIONS,
            ROLES.ADMIN: ADMIN_PERMISSIONS,
            ROLES.MEMBER: MEMBER_PERMISSIONS}
