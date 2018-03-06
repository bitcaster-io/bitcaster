# -*- coding: utf-8 -*-
import json
import logging
from enum import Enum

from cryptography.fernet import Fernet, MultiFernet
from django.conf import settings
from django.contrib.postgres.fields import JSONField as _JSONField
from django.contrib.postgres.forms import JSONField as _JSONFormField
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from fernet_fields import hkdf
from jsoneditor.forms import JSONEditor
from picklefield import PickledObjectField

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


class LanguageField(models.CharField):
    """
    A language field for Django models.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 5)
        kwargs.setdefault('choices', settings.LANGUAGES)
        super().__init__(*args, **kwargs)


class EncryptedPickledObjectField(PickledObjectField):

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
        return json.loads(self.fernet.decrypt(value.encode("utf8")))

    def get_prep_value(self, value):
        value = self.fernet.encrypt(value.encode("utf8")).decode("utf8")
        return super().get_prep_value(value)


class DeletionStatus(Enum):
    ACTIVE = 1
    PENDING_DELETION = 2
    DELETION_IN_PROGRESS = 3
    DEPRECATED = 4

    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __int__(self):
        return self.value

    @classmethod
    def as_choices(cls):
        return sorted([(cls.VISIBLE, _('Active')),
                       (cls.DEPRECATED, _('Deprecated')),
                       (cls.PENDING_DELETION, _('Pending Deletion')),
                       (cls.DELETION_IN_PROGRESS, _('Deletion in Progress')),
                       ])


class DeleteableModelManagerMixin(models.QuerySet):
    def valid(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class DeletionStatusField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, primary_key=False, max_length=None, unique=False,
                 blank=False, null=False, db_index=False, rel=None, default=DeletionStatus.VISIBLE,
                 editable=True, serialize=True, unique_for_date=None, unique_for_month=None, unique_for_year=None,
                 choices=DeletionStatus.as_choices(), help_text='',
                 db_column=None, db_tablespace=None, auto_created=False, validators=(), error_messages=None):
        super().__init__(verbose_name, name, primary_key, max_length, unique, blank, null, db_index, rel, default,
                         editable, serialize, unique_for_date, unique_for_month, unique_for_year, choices, help_text,
                         db_column, db_tablespace, auto_created, validators, error_messages)
