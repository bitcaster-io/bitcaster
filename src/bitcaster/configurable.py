import logging
from collections import OrderedDict

from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.serializers import Serializer

from bitcaster.exceptions import PluginValidationError
from bitcaster.utils.language import classproperty
from bitcaster.utils.reflect import fqn, package_name

logger = logging.getLogger(__name__)


class ConfigurableOptionsForm(serializers.Serializer):
    """
        fieldsets = {'common': ['fieldname1',...],
                     'security': ['fieldname11',...],
                    }
    """
    fieldset_defs = None
    default_section_title = _('Handler Settings')
    missing_section_title = _('Other')

    @cached_property
    def fieldsets(self):
        ret = OrderedDict()
        if self.fieldset_defs:
            added = []
            _fields = {f.name: f for f in self}

            for group_name, fieldnames in self.fieldset_defs:
                ret[group_name] = []
                for field_name in fieldnames:
                    ret[group_name].append(_fields[field_name])
                    added.append(field_name)

            remaining = []
            for field_name, field in _fields.items():
                if field_name not in added:
                    remaining.append(_fields[field_name])
            if remaining:
                ret[self.missing_section_title] = remaining
        else:
            ret[self.default_section_title] = [f for f in self]
        return ret


def get_configuration(serializer_class: type(Serializer), config: dict,
                      raise_exception=None):
    try:
        ser = serializer_class(data=config)
        valid = ser.is_valid(raise_exception)
        errors = dict(ser.errors)
        for field_name in config.keys():
            if field_name not in ser.fields:
                valid = False
                errors[field_name] = ['Unknown attribute `%s`' % field_name]
        if not valid and raise_exception:
            raise PluginValidationError(errors)
        return (valid, errors)
    except ValidationError as e:
        if raise_exception:
            raise PluginValidationError(e)


def get_config_defaults(serializer_class: type(Serializer)):
    ret = {}
    ser = serializer_class(data={})
    for name, f in ser.fields.items():
        ret[name] = '' if f.default == empty else f.default
    return ret


def get_full_config(serializer_class: type(Serializer), values: dict = None):
    updates = values or {}
    return {**get_config_defaults(serializer_class), **updates}


class ConfigurableMixin:
    options_class = None
    __license__ = 'MIT'
    __author__ = ''
    __help__ = ''
    __url__ = ''
    __core__ = False

    def __init__(self, owner=None):
        self.owner = owner
        self._config = None

    @classproperty
    def fqn(cls):
        return fqn(cls)

    def get_options_form(self, **kwargs):
        if self.owner:
            kwargs.setdefault('data', self.owner.config)
        return self.options_class(**kwargs)

    @classmethod
    def get_full_config(cls, custom=None):
        updates = custom or {}
        return {**get_config_defaults(cls.options_class), **updates}

    @classproperty
    def name(cls):
        return cls.__name__

    @classproperty
    def author(cls):
        return cls.__author__

    @classproperty
    def url(cls):
        return cls.__url__

    @classproperty
    def help(cls):
        return cls.__help__

    @classproperty
    def version(cls):
        try:
            import pkg_resources  # part of setuptools
            return pkg_resources.require(package_name(cls))[0].version
        except Exception:
            return f'unknown'

    @classproperty
    def license(cls):
        return cls.__license__

    @classmethod
    def validate_configuration(self, config, raise_exception=True, *args, **kwargs) -> None:
        cfg = get_full_config(self.options_class, config)
        opts = self.options_class(data=cfg)
        return opts.is_valid(raise_exception)

    @property
    def config(self):
        if self._config is None:
            self._config = self._configure()
        return self._config

    def _configure(self):
        if self.options_class:
            cfg = get_full_config(self.options_class, self.owner.config)
            opts = self.get_options_form(data=cfg)
            if opts.is_valid():
                return opts.data
            else:
                logger.error('Invalid configuration %s ' % opts.errors)
                raise PluginValidationError(opts.errors)
        return {}
