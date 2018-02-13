# -*- coding: utf-8 -*-
import json
import logging
from django.conf import settings
from django.contrib.postgres.fields import JSONField as _JSONField
from django.contrib.postgres.forms import JSONField as _JSONFormField
from django.utils.functional import cached_property

from cryptography.fernet import Fernet, MultiFernet
from fernet_fields import hkdf
from jsoneditor.forms import JSONEditor

logger = logging.getLogger(__name__)


class JSONFormField(_JSONFormField):
    widget = JSONEditor

    def __init__(self, *av, **kw):
        kw['widget'] = self.widget  # force avoiding widget override
        super(JSONFormField, self).__init__(*av, **kw)


class EncryptedJSONField(_JSONField):

    @cached_property
    def keys(self):
        keys = getattr(settings, 'FERNET_KEYS', None)
        if keys is None:
            keys = [settings.SECRET_KEY]
        return keys

    @cached_property
    def fernet_keys(self):
        if getattr(settings, 'FERNET_USE_HKDF', True):
            return [hkdf.derive_fernet_key(k) for k in self.keys]
        return self.keys

    @cached_property
    def fernet(self):
        if len(self.fernet_keys) == 1:
            return Fernet(self.fernet_keys[0])
        return MultiFernet([Fernet(k) for k in self.fernet_keys])

    def from_db_value(self, value, expression, connection, context):
        return json.loads(self.fernet.decrypt(value["f"].encode("utf8")))

    def get_prep_value(self, value):
        value = {'f': self.fernet.encrypt(json.dumps(value).encode("utf8")).decode("utf8")}
        return super().get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': kwargs.get('form_class', JSONFormField),
        }
        defaults.update(kwargs)
        return super(EncryptedJSONField, self).formfield(**defaults)
