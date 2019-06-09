import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from bitcaster.framework.db.fields import APP_ROLES, ORG_ROLES
from bitcaster.models import Application, Event, Organization
from bitcaster.security import ORG_PERMISSIONS, PERM_MAP

logger = logging.getLogger(__name__)


# TARGETS = ['system', 'org', 'app']

class BitcasterBackend:

    def authenticate(self, request, username=None, password=None, **kwargs):
        return None

    def get_user(self, *args):
        return None

    def get_all_permissions(self, user_obj, obj=None):
        perms = []
        roles = []
        if isinstance(obj, Application):
            org = obj.organization
            if org.owner == user_obj or user_obj in org.owners:
                roles.append(ORG_ROLES.OWNER)
                if user_obj in obj.admins:
                    roles = [APP_ROLES.ADMINS]
        elif isinstance(obj, Organization):
            if obj.owner == user_obj or user_obj in obj.owners:
                roles += [ORG_ROLES.OWNER]
            if user_obj in obj.supervisors:
                roles += [ORG_ROLES.SUPERVISOR]
        for r in roles:
            perms.extend(PERM_MAP[r])
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
                if perm not in ORG_PERMISSIONS:
                    return True
                return perm in self.get_all_permissions(user_obj, obj)
            elif isinstance(obj, Application):
                return (obj.organization.owner == user_obj or
                        user_obj in obj.organization.managers or
                        user_obj in obj.owners or
                        user_obj in obj.admins)
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
                        role__in=[APP_ROLES.ADMIN]
                    ).exists()
                    # applicationteam = app.application_teams.get(role=ROLES.ADMIN)
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
