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
    def __init__(self, backend):
        self.backend = backend

    def __str__(self):
        return 'User doesn\'t belong to the organization'


class MaxChannelError(Exception):
    def __init__(self, channel):
        self.channel = channel

    def __str__(self):
        return f'Channel {self.channel} max allowed errors'
