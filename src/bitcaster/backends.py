# -*- coding: utf-8 -*-
import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from bitcaster.db.fields import Role
from bitcaster.models import Application, Event, Organization

logger = logging.getLogger(__name__)

TARGETS = ['system', 'org', 'app']

PERMISSIONS = {'org:configure',  # configure
               'app:create',  # create applications
               'app:configure',  # configure application (#General, create channels)
               'app:manage',  # manage application (manage events/messages
               }

OWNER_PERMISSIONS = PERMISSIONS
ADMIN_PERMISSIONS = {'app:configure', 'evt:trigger'}
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
        if isinstance(obj, (Event, Application)):
            if isinstance(obj, Event):
                obj = obj.application
            org = obj.organization
            roles = list(obj.application_teams.filter(
                team__members__user=user_obj,
                role__in=[Role.ADMIN, Role.OWNER]
            ).values_list('role', flat=True))
            if user_obj == org.owner:
                roles.append(Role.OWNER)

        elif isinstance(obj, Organization):
            if user_obj == obj.owner:
                roles = [Role.OWNER]

        [perms.extend(list(PERM_MAP[x])) for x in roles]
        return set(perms)

    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        # if perm not in PERMISSIONS:
        #     return False

        if user_obj.is_superuser:
            return True
        # TODO: remove me
        print(111, 'backends.py:76', 111111, user_obj, perm)
        if obj:
            if isinstance(obj, Organization):
                return obj.owner == user_obj or user_obj in obj.owners
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
