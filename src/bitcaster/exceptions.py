# -*- coding: utf-8 -*-
from rest_framework.exceptions import ValidationError as DRFValidationError
from social_core.exceptions import AuthFailed


class BitcasterError(Exception):
    pass


class UnableToAcquireLock(BitcasterError):
    """Exception raised when a lock cannot be acquired."""


class PluginValidationError(DRFValidationError):
    pass


class PluginSubscriptionError(BitcasterError):
    pass


class PluginSendError(BitcasterError):
    pass


class LogicError(BitcasterError):
    pass


class InvalidRecipient(BitcasterError):
    pass


class ImproperlyConfigured(BitcasterError):
    pass


class RecipientNotFound(InvalidRecipient):
    pass


class HandlerNotFound(ImportError):
    pass


class OAuthError(Exception):
    pass


class NotMemberOfOrganization(AuthFailed):
    pass
