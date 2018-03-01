# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.backends import ModelBackend

from mercury.models import Application, Organization

logger = logging.getLogger(__name__)


class BitcasterBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        if isinstance(obj, (Organization, Application)):
            return True

        return None
