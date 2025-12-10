from typing import TypeVar

from django.core.mail.backends.base import BaseEmailBackend

from bitcaster.dispatchers.base import DispatcherConfig

TDispatcherConfig_co = TypeVar("TDispatcherConfig_co", bound=DispatcherConfig, covariant=True)
TBaseEmailBackend_co = TypeVar("TBaseEmailBackend_co", bound=BaseEmailBackend, covariant=True)

DispatcherHandler = BaseEmailBackend
