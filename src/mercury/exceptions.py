# -*- coding: utf-8 -*-
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError

class MercuryError(Exception):
    pass


class UnableToAcquireLock(MercuryError):
    """Exception raised when a lock cannot be acquired."""


class PluginValidationError(DRFValidationError, ValidationError):
    pass


class PluginSendError(MercuryError):
    pass


class LogicError(MercuryError):
    pass


class ValidationError(DRFValidationError):
    pass
