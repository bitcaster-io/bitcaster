# -*- coding: utf-8 -*-
import logging

from django.template import Context

from bitcaster.logging import secLog

logger = logging.getLogger(__name__)


class Stop:
    def __repr__(self):
        return ''

    def __str__(self):
        return ''


class Wrapper:
    def __init__(self, wrapped):
        self.__wrapped = wrapped

    def _path(self):
        pass

    def __getattr__(self, item):
        if isinstance(self.__wrapped, Stop):
            return Wrapper('*******')

        if item in ['key', 'token', 'password', 'handler', 'owner']:
            secLog.error(f'Access forbidden attribute `{item}`',
                         extra={'attribute': item,
                                'object': self.__wrapped})
            return '******'
        original = getattr(self.__wrapped, item)
        if callable(original):
            secLog.error(f'Access forbidden attribute `{item}`',
                         extra={'attribute': item,
                                'object': self.__wrapped})
            return Wrapper(Stop())

        return Wrapper(original)

    def __repr__(self):
        return repr(self.__wrapped)

    def __str__(self):
        return str(self.__wrapped)


class SecureContext(Context):
    def __getitem__(self, key):
        return Wrapper(super().__getitem__(key))
