# -*- coding: utf-8 -*-
import logging
from functools import wraps

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden

logger = logging.getLogger(__name__)


def is_member_of(user, organization):
    return organization.members.filter(pk=user.pk).exists()


def is_owner(user, organization):
    return organization.owners.filter(pk=user.pk).exists()


def is_anonymous(function):
    actual_decorator = user_passes_test(
        lambda u: u.is_anonymous
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def authorized_or_403(test_func):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden()

        return _wrapped_view

    return decorator
