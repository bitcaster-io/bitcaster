# -*- coding: utf-8 -*-
from rest_framework.exceptions import ValidationError as DRFValidationError


class MercuryError(Exception):
    pass


class UnableToAcquireLock(MercuryError):
    """Exception raised when a lock cannot be acquired."""


class PluginValidationError(DRFValidationError):
    pass


class PluginSubscriptionError(MercuryError):
    pass


class PluginSendError(MercuryError):
    pass


class LogicError(MercuryError):
    pass


class InvalidRecipient(MercuryError):
    pass


class ImproperlyConfigured(MercuryError):
    pass


class RecipientNotFound(InvalidRecipient):
    pass


class HandlerNotFound(ImportError):
    pass


class OAuthError(Exception):
    pass
