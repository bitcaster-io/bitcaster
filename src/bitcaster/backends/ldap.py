# -*- coding: utf-8 -*-
import logging

import django.conf
from constance import config
from django_auth_ldap.backend import LDAPBackend, LDAPSettings as _LDAPSettings

logger = logging.getLogger(__name__)


class LDAPSettings(_LDAPSettings):
    def __init__(self, prefix='AUTH_LDAP_', defaults={'USER_ATTR_MAP': {'email': 'cn'},
                                                      }):
        self._prefix = prefix

        defaults = dict(self.defaults, **defaults)

        for name, default in defaults.items():
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
                pass
        return None
