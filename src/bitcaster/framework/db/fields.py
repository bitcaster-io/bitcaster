import base64
import json
import logging

from cryptography.fernet import Fernet, MultiFernet
from django.conf import settings
from django.contrib.postgres.fields import JSONField as _JSONField
# from django.contrib.postgres.forms import JSONField as _JSONFormField
from django.db import models
from django.db.models import Field
from django.utils.functional import cached_property
from fernet_fields import hkdf
# from jsoneditor.forms import JSONEditor
from strategy_field.fields import StrategyField

from bitcaster.agents.registry import agent_registry
from bitcaster.attachments.registry import registry as retriever_registry
from bitcaster.dispatchers import dispatcher_registry
from bitcaster.exceptions import HandlerNotFound
from bitcaster.file_storage import AvatarFileSystemStorage
# from bitcaster.web.forms.fields.d import DispatcherFormField
from bitcaster.security import ROLES

from ..forms.fields import DispatcherFormField

logger = logging.getLogger(__name__)


class EncryptedJSONField(_JSONField):

    @cached_property
    def keys(self):
        keys = getattr(settings, 'FERNET_KEYS', None)
        if keys is None:
            keys = [base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32])]
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
        return json.loads(self.fernet.decrypt(value['f'].encode('utf8')))

    def get_prep_value(self, value):
        value = {'f': self.fernet.encrypt(json.dumps(value).encode('utf8')).decode('utf8')}
        return super().get_prep_value(value)

    # def formfield(self, **kwargs):
    #     defaults = {
    #         'form_class': kwargs.get('form_class', JSONFormField),
    #     }
    #     defaults.update(kwargs)
    #     return super(EncryptedJSONField, self).formfield(**defaults)


class LanguageField(models.CharField):
    """
    A language field for Django models.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 5)
        kwargs.setdefault('choices', settings.LANGUAGES)
        super().__init__(*args, **kwargs)


# class DeletionStatus(EnumField):
#     ACTIVE = 1
#     PENDING_DELETION = 2
#     DELETION_IN_PROGRESS = 3
#     DEPRECATED = 4
#
#     @classmethod
#     def as_choices(cls):
#         return sorted([(int(cls.ACTIVE), _('Active')),
#                        (int(cls.DEPRECATED), _('Deprecated')),
#                        (int(cls.PENDING_DELETION), _('Pending Deletion')),
#                        (int(cls.DELETION_IN_PROGRESS), _('Deletion in Progress')),
#                        ])


# class DeletionStatusField(models.IntegerField):
#     def __init__(self, verbose_name=None, name=None, db_index=False, serialize=True,
#                  choices=DeletionStatus.as_choices(),
#                  default=DeletionStatus.ACTIVE,
#                  help_text='', db_column=None, db_tablespace=None, validators=(), error_messages=None):
#         super().__init__(verbose_name=verbose_name, name=name,
#                          choices=choices,
#                          db_index=db_index, serialize=serialize, default=default,
#                          help_text=help_text,
#                          db_column=db_column, db_tablespace=db_tablespace, validators=validators,
#                          error_messages=error_messages)
#
#     def get_prep_value(self, value):
#         return super().get_prep_value(int(value))
#
#     def value_to_string(self, obj):
#         """
#         Return a string value of this field from the passed obj.
#         This is used by the serialization framework.
#         """
#         return str(int(self.value_from_object(obj)))


class RoleField(models.IntegerField):
    def __init__(self, verbose_name=None, name=None, db_index=False, serialize=True,
                 choices=ROLES,
                 default=ROLES.MEMBER,
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


def handler_not_found(fqn, exc):  # pragma: no cover
    try:
        raise HandlerNotFound(fqn) from exc
    except HandlerNotFound as e:
        logger.exception(e)
    return None


class DispatcherField(StrategyField):
    form_class = DispatcherFormField

    def __init__(self, **kwargs):
        kwargs.setdefault('verbose_name', 'Dispatcher')
        kwargs.setdefault('display_attribute', 'name')
        kwargs.setdefault('import_error', handler_not_found)
        kwargs.setdefault('registry', dispatcher_registry)
        super().__init__(**kwargs)

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.creation_counter == other.creation_counter

    def formfield(self, form_class=None, choices_form_class=None, **kwargs):
        return super().formfield(form_class, choices_form_class, **kwargs)

    def __hash__(self):
        return hash(self.__str__())


class AgentField(StrategyField):

    def __init__(self, **kwargs):
        kwargs.setdefault('verbose_name', 'Agent')
        kwargs.setdefault('display_attribute', 'name')
        kwargs.setdefault('import_error', handler_not_found)
        kwargs.setdefault('registry', agent_registry)
        super().__init__(**kwargs)

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.creation_counter == other.creation_counter


class AvatarField(models.ImageField):

    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs.setdefault('blank', True)
        kwargs.setdefault('null', True)
        kwargs.setdefault('storage', AvatarFileSystemStorage())
        kwargs.setdefault('height_field', 'picture_height')
        kwargs.setdefault('width_field', 'picture_width')
        super().__init__(verbose_name, name, **kwargs)


class RetrieverField(StrategyField):
    # form_class = RetrieverFormField

    def __init__(self, **kwargs):
        kwargs.setdefault('verbose_name', 'Retriever')
        kwargs.setdefault('display_attribute', 'name')
        kwargs.setdefault('import_error', handler_not_found)
        kwargs.setdefault('registry', retriever_registry)
        super().__init__(**kwargs)

    def __eq__(self, other):
        if isinstance(other, Field):
            return self.creation_counter == other.creation_counter

    def formfield(self, form_class=None, choices_form_class=None, **kwargs):
        return super().formfield(form_class, choices_form_class, **kwargs)

    def __hash__(self):
        return hash(self.__str__())
