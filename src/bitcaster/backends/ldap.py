# -*- coding: utf-8 -*-
import logging

import django.conf
from constance import config
from django.core.exceptions import ObjectDoesNotExist
from django_auth_ldap.backend import (LDAPBackend,
                                      LDAPSettings as _LDAPSettings, _LDAPUser,)

logger = logging.getLogger(__name__)


class LDAPSettings(_LDAPSettings):
    def __init__(self, prefix='AUTH_LDAP_', defaults=None):
        self._prefix = prefix

        values = dict(self.defaults, **(defaults or {}))

        for name, default in values.items():
            fullname = prefix + name
            if fullname in django.conf.settings.CONSTANCE_CONFIG:
                value = getattr(config, fullname)
            else:
                value = getattr(django.conf.settings, fullname, default)
            setattr(self, name, value)


class BitcasterLDAPBackend(LDAPBackend):
    @property
    def settings(self):
        if self._settings is None:
            self._settings = LDAPSettings(self.settings_prefix,
                                          self.default_settings)

        return self._settings

    def authenticate(self, request, username=None, password=None, **kwargs):
        if config.AUTH_LDAP_ENABLE:
            try:
                return super().authenticate(request, username, password, **kwargs)
            except Exception as e:
                logger.error(e)
        return None

    def get_user(self, user_id):
        user = None

        try:
            user = self.get_user_model().objects.get(pk=user_id)
            _LDAPUser(self, user=user)  # This sets user.ldap_user
        except ObjectDoesNotExist:
            pass

        return user

    def populate_user(self, username):
        ldap_user = _LDAPUser(self, username=username)
        user = ldap_user.populate_user()

        return user
