# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


def is_member_of(user, organization):
    return organization.members.filter(pk=user.pk).exists()


def is_owner(user, organization):
    return organization.owners.filter(pk=user.pk).exists()
