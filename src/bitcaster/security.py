import logging

from django.utils.translation import gettext_lazy as _
from model_utils import Choices

logger = logging.getLogger(__name__)

ROLE_SUPERUSER = -1
ROLE_OWNER = 1
ROLE_SUPERVISOR = 2
ROLE_MEMBER = 4
ROLE_ADMIN = 100
ROLE_USER = 101

ORG_ROLES = Choices(
    (ROLE_SUPERUSER, 'SUPERUSER', _('Superuser')),  # Access to system settings
    (ROLE_OWNER, 'OWNER', _('Owner')),  # Organization Owner
    (ROLE_SUPERVISOR, 'SUPERVISOR', _('Supervisor')),  # Organization Supervisor
    (ROLE_MEMBER, 'MEMBER', _('Member'))
)

APP_ROLES = Choices(
    (ROLE_ADMIN, 'ADMIN', _('Admin')),  # Application Admin
    (ROLE_USER, 'USER', _('User'))
)

ALL_PERMISSIONS = set()
ORG_PERMISSIONS = {'manage_organization',
                   'create_channel',
                   'edit_channel',
                   'create_application',
                   'manage_application',
                   'invite_member',  # invite new Organization member from within an app
                   'manage_monitor',
                   }
APP_PERMISSIONS = {'manage_application',
                   'manage_monitor',
                   }

OWNER_PERMISSIONS = ORG_PERMISSIONS
SUPERVISOR_PERMISSIONS = ORG_PERMISSIONS
ADMIN_PERMISSIONS = APP_PERMISSIONS
USER_PERMISSIONS = set()
MEMBER_PERMISSIONS = set()

ALL_PERMISSIONS.update(ORG_PERMISSIONS)
ALL_PERMISSIONS.update(APP_PERMISSIONS)
ALL_PERMISSIONS.add('admin_system')

PERM_MAP = {ORG_ROLES.OWNER: OWNER_PERMISSIONS,
            ORG_ROLES.SUPERVISOR: SUPERVISOR_PERMISSIONS,
            ORG_ROLES.MEMBER: MEMBER_PERMISSIONS,
            APP_ROLES.ADMIN: ADMIN_PERMISSIONS,
            APP_ROLES.USER: USER_PERMISSIONS,
            }
