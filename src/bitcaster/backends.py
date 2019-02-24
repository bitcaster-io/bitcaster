# -*- coding: utf-8 -*-
import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from bitcaster.db.fields import Role
from bitcaster.models import Application, Event, Organization

logger = logging.getLogger(__name__)

TARGETS = ['system', 'org', 'app']

PERMISSIONS = {'org:configure',  # configure
               'org:create_channel',
               'app:create',  # create applications
               'app:configure',  # configure application (#General, create channels)
               'app:manage',  # manage application (manage events/messages
               'evt:trigger'
               }

OWNER_PERMISSIONS = PERMISSIONS
ADMIN_PERMISSIONS = {'org:configure', 'app:configure', 'evt:trigger'}
SUBSCRIBER_PERMISSIONS = ()
PERM_MAP = {Role.ADMIN: ADMIN_PERMISSIONS,
            Role.OWNER: OWNER_PERMISSIONS,
            Role.SUBSCRIBER: SUBSCRIBER_PERMISSIONS}


class BitcasterBackend:

    # def __init__(self) -> None:
    #     super().__init__()

    def authenticate(self, request, username=None, password=None, **kwargs):
        return None

    # @cached_property
    # def app_manager(self):
    #     return AppRulesManager()
    #
    # @cached_property
    # def org_manager(self):
    #     return OrgRulesManager()
    def get_user(self, *args):
        return None

    def get_all_permissions(self, user_obj, obj=None):
        perms = []
        roles = []
        if isinstance(obj, Application):
            org = obj.organization
            if org.owner == user_obj or user_obj in org.owners:
                roles.append(Role.OWNER)
            if user_obj in obj.admins:
                roles = [Role.ADMIN]

            [perms.extend(list(PERM_MAP[x])) for x in roles]
        elif isinstance(obj, Event):
            org = obj.application.organization
            if org.owner == user_obj or user_obj in org.owners:
                roles = [Role.OWNER]
            if user_obj in obj.application.admins:
                roles = [Role.ADMIN]

            [perms.extend(list(PERM_MAP[x])) for x in roles]

        elif isinstance(obj, Organization):
            if obj.owner == user_obj or user_obj in obj.owners:
                roles += [Role.OWNER]
            if user_obj in obj.admins:
                roles += [Role.ADMIN]
            [perms.extend(list(PERM_MAP[x])) for x in roles]

        return set(perms)

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        # if perm not in PERMISSIONS:
        #     return False

        if user_obj.is_superuser:
            return True
        if obj:
            if isinstance(obj, Organization):
                return perm in self.get_all_permissions(user_obj, obj)
            elif isinstance(obj, Application):
                return (obj.organization.owner == user_obj or
                        user_obj in obj.organization.managers or
                        user_obj in obj.owners)
            elif isinstance(obj, Event):
                app = obj.application
                org = app.organization
                User = get_user_model()
                User.objects.filter(memberships__team__applicationteam__application=app)
                try:
                    # get
                    if user_obj == org.owner:
                        return True
                    return app.application_teams.filter(
                        team__members__user=user_obj,
                        role__in=[Role.ADMIN, Role.OWNER]
                    ).exists()
                    # applicationteam = app.application_teams.get(role=Role.ADMIN)
                    # return applicationteam.members.filter(user=user_obj).exists()

                except ObjectDoesNotExist:
                    return False
            return None

        return None

    def admins(self, application):
        return []

    def owners(self, application):
        return []

    def members(self, application):
        return []

    def subscribers(self, application):
        return []
