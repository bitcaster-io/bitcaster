# -*- coding: utf-8 -*-
import logging
from functools import wraps

from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)


# def is_member_of(user, organization):
#     return organization.members.filter(pk=user.pk).exists()

#
# def is_owner(user, target):
#     # FIXME
#     if hasattr(target, 'organization'):
#         org = target.organization
#         return org.owner == user or target.membership_for(user).role == Role.OWNER
#     else:
#         return target.owner == user or target.membership_for(user).role == Role.OWNER
#     # return organization.owners.filter(pk=user.pk).exists()


# def is_admin(user, organization):
#     return organization.membership_for(user).role == Role.ADMIN
# return organization.admins.filter(pk=user.pk).exists()

#
# def is_manager(user, organization):
#     try:
#         return organization.membership_for(user).role in [Role.ADMIN, Role.OWNER]
#     except AttributeError:
#         return user.is_superuser
#     # return organization.admins.filter(pk=user.pk).exists()


def authorized_or_403(test_func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()

        return _wrapped_view

    return decorator
