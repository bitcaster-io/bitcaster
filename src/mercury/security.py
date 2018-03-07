# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.decorators import user_passes_test

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
