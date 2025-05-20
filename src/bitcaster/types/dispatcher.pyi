from typing import TypeVar

from django.core.mail.backends.base import BaseEmailBackend

from bitcaster.dispatchers.base import DispatcherConfig

TDispatcherConfig = TypeVar("TDispatcherConfig", bound=DispatcherConfig, covariant=True)
TBaseEmailBackend = TypeVar("TBaseEmailBackend", bound=BaseEmailBackend, covariant=True)

DispatcherHandler = BaseEmailBackend
