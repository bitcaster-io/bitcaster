# -*- coding: utf-8 -*-
"""
mercury / security
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

logger = logging.getLogger(__name__)


def is_member_of(user, organization):
    return organization.members.filter(pk=user.pk).exists()
