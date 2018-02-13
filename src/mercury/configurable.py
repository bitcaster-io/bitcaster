from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty

from mercury import logging
from mercury.exceptions import PluginValidationError
from mercury.utils.language import classproperty

logger = logging.getLogger(__name__)


class ConfigurableMixin:
    options_class = None
    __license__ = 'MIT'
    __author__ = 'unknown'

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
    def license(cls):
        return cls.__license__

    def get_full_config(self, custom):
        updates = custom or {}
        return {**self.defaults(), **updates}

    @classmethod
    def defaults(cls):
        ret = {}
        if cls.options_class:
            ser = cls.options_class(data={})
            for name, f in ser.fields.items():
                ret[name] = '' if f.default == empty else f.default
        return ret

    @classmethod
    def validate_configuration(self, config, raise_exception=False):
        if self.options_class:
            try:
                ser = self.options_class(data=config)
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
                raise PluginValidationError(e)
        return True, []

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
