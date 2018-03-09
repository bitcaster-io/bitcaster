from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.serializers import Serializer

from bitcaster import logging
from bitcaster.exceptions import PluginValidationError
from bitcaster.utils.language import classproperty
from bitcaster.utils.reflect import package_name

logger = logging.getLogger(__name__)


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
    __author__ = 'unknown'
    __help__ = ""
    __url__ = ""

    def __init__(self, owner=None):
        self.owner = owner
        self._config = None

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
            return f"unknown"

    @classproperty
    def license(cls):
        return cls.__license__

    def get_full_config(self, custom):
        updates = custom or {}
        return {**get_config_defaults(self.options_class), **updates}

    # @classmethod
    # def defaults(cls):
    #     ret = {}
    #     if cls.options_class:
    #         ser = cls.options_class(data={})
    #         for name, f in ser.fields.items():
    #             ret[name] = '' if f.default == empty else f.default
    #     return ret

    # @classmethod
    # def validate_configuration(self, config, raise_exception=False):
    #     if self.options_class:
    #         try:
    #             ser = self.options_class(data=config)
    #             valid = ser.is_valid(raise_exception)
    #             errors = dict(ser.errors)
    #             for field_name in config.keys():
    #                 if field_name not in ser.fields:
    #                     valid = False
    #                     errors[field_name] = ['Unknown attribute `%s`' % field_name]
    #             if not valid and raise_exception:
    #                 raise PluginValidationError(errors)
    #             return (valid, errors)
    #         except ValidationError as e:
    #             if raise_exception:
    #                 raise PluginValidationError(e)
    #     return True, []

    @classmethod
    def validate_configuration(self, config, raise_exception=True, *args, **kwargs) -> None:
        cfg = get_full_config(self.options_class, config)
        return self.options_class(data=cfg).is_valid(raise_exception)

    @property
    def config(self):
        if self._config is None:
            self._config = self._configure()
        return self._config

    def _configure(self):
        if self.options_class:
            opts = self.options_class(data=self.owner.config)
            if opts.is_valid():
                return opts.data
            else:
                logger.error("Invalid configuration %s " % opts.errors)
                raise PluginValidationError(opts.errors)
        return {}
