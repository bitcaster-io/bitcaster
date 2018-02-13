# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError as _ValidationError

from rest_framework.exceptions import ValidationError as DRFValidationError


class MercuryError(Exception):
    pass


class UnableToAcquireLock(MercuryError):
    """Exception raised when a lock cannot be acquired."""


class PluginValidationError(DRFValidationError, _ValidationError):
    pass


class PluginSendError(MercuryError):
    pass


class LogicError(MercuryError):
    pass

#
# class ValidationError(DRFValidationError):
#     pass
