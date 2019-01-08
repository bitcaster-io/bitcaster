# -*- coding: utf-8 -*-
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist
from django.utils.functional import cached_property

from bitcaster.db.fields import Role
from bitcaster.models import Application, Event, Organization

logger = logging.getLogger(__name__)

PERMISSIONS = {'org:configure',  # configure
               'app:create',  # create applications
               'app:configure',  # configure application (#General, create channels)
               'app:manage',  # manage application (manage events/messages
               'evt:trigger',  # trigger events (need triggertoken
               }
OWNER_PERMISSIONS = PERMISSIONS
ADMIN_PERMISSIONS = {'app:configure', 'evt:trigger'}
SUBSCRIBER_PERMISSIONS = ()
PERM_MAP = {Role.ADMIN: ADMIN_PERMISSIONS,
            Role.OWNER: OWNER_PERMISSIONS,
            Role.SUBSCRIBER: SUBSCRIBER_PERMISSIONS}


class RulesManager:
    def has_perm(self, user_obj, perm, obj):
        pass


class OrgRulesManager(RulesManager):
    pass


class AppRulesManager(RulesManager):
    pass


class BitcasterBackend(ModelBackend):

    def __init__(self) -> None:
        super().__init__()

    @cached_property
    def app_manager(self):
        return AppRulesManager()

    @cached_property
    def org_manager(self):
        return OrgRulesManager()

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

        if obj:
            if isinstance(obj, Event):
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
            return True

        return None

    def admins(self, application):
        return []

    def owners(self, application):
        return []

    def members(self, application):
        return []

    def subscribers(self, application):
        return []
