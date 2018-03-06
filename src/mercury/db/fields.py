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

    def __gt__(self, other):
        return int(self) > int(other)

    def __lt__(self, other):
        return int(self) < int(other)

    @classmethod
    def as_choices(cls):
        return sorted([(int(cls.ACTIVE), _('Active')),
                       (int(cls.DEPRECATED), _('Deprecated')),
                       (int(cls.PENDING_DELETION), _('Pending Deletion')),
                       (int(cls.DELETION_IN_PROGRESS), _('Deletion in Progress')),
                       ])


class DeleteableModelManagerMixin(models.QuerySet):
    def valid(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class DeletionStatusField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, db_index=False, serialize=True,
                 choices=DeletionStatus.as_choices(),
                 default=int(DeletionStatus.ACTIVE),
                 help_text='', db_column=None, db_tablespace=None, validators=(), error_messages=None):
        super().__init__(verbose_name=verbose_name, name=name,
                         choices=choices,
                         db_index=db_index, serialize=serialize, default=default,
                         help_text=help_text,
                         db_column=db_column, db_tablespace=db_tablespace, validators=validators,
                         error_messages=error_messages)


class Role(Enum):
    OWNER = 1
    ADMIN = 2
    MEMBER = 3
    RECIPIENT = 4

    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        return member

    def __str__(self):
        return str(self)

    def __int__(self):
        return self.value

    def __eq__(self, other):

        return int(self) == int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __lt__(self, other):
        return int(self) < int(other)

    @classmethod
    def as_choices(cls):
        return sorted([(int(cls.OWNER), _('Owner')),
                       (int(cls.ADMIN), _('Admin')),
                       (int(cls.MEMBER), _('Member')),
                       (int(cls.RECIPIENT), _('Recipient')),
                       ])


class RoleField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, db_index=False, serialize=True,
                 choices=Role.as_choices(),
                 default=int(Role.MEMBER),
                 help_text='', db_column=None, db_tablespace=None, validators=(), error_messages=None):
        super().__init__(verbose_name=verbose_name, name=name,
                         choices=choices,
                         db_index=db_index, serialize=serialize, default=default,
                         help_text=help_text,
                         db_column=db_column, db_tablespace=db_tablespace, validators=validators,
                         error_messages=error_messages)

    def get_prep_value(self, value):
        return super().get_prep_value(int(value))

    def value_to_string(self, obj):
        """
        Return a string value of this field from the passed obj.
        This is used by the serialization framework.
        """
        return str(int(self.value_from_object(obj)))
