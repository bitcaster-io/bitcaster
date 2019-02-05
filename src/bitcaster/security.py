# -*- coding: utf-8 -*-
import logging
from functools import wraps

from django.http import HttpResponseForbidden

from bitcaster.db.fields import Role

logger = logging.getLogger(__name__)


# def is_member_of(user, organization):
#     return organization.members.filter(pk=user.pk).exists()


def is_owner(user, organization):
    return organization.membership_for(user).role == Role.OWNER
    # return organization.owners.filter(pk=user.pk).exists()


# def is_admin(user, organization):
#     return organization.membership_for(user).role == Role.ADMIN
    # return organization.admins.filter(pk=user.pk).exists()


def is_manager(user, organization):
    try:
        return organization.membership_for(user).role in [Role.ADMIN, Role.OWNER]
    except AttributeError:
        return False
    # return organization.admins.filter(pk=user.pk).exists()


def authorized_or_403(test_func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()

        return _wrapped_view

    return decorator
