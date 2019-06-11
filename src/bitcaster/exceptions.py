from django.core.exceptions import PermissionDenied as _PermissionDenied
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError as DRFValidationError
from social_core.exceptions import AuthFailed

from bitcaster.utils.language import repr_list


class BitcasterError(Exception):
    pass


class UnableToAcquireLock(BitcasterError):
    """Exception raised when a lock cannot be acquired."""


class PluginValidationError(DRFValidationError):
    pass


class PluginError(BitcasterError):
    pass


class PluginSubscriptionError(BitcasterError):
    pass


class PluginSendError(BitcasterError):
    def __init__(self, message, **kwargs):
        self.message = str(message)
        self.extra = kwargs

    def __str__(self):
        return self.message


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
    def __init__(self, org_name):
        self.org_name = org_name

    def __str__(self):
        return _('Sorry, you do not seem to be a public member of %s' % self.org_name)


class MaxChannelError(Exception):
    def __init__(self, channel):
        self.channel = channel

    def __str__(self):
        return f'Channel {self.channel} max allowed errors'


class PermissionDenied(_PermissionDenied):
    def __init__(self, view, obj, message=None):
        self.view = view
        self.target = obj
        self.message = message or ('You do not have required permission %s on %s' %
                                   (repr_list(view.permissions), obj))

    def __str__(self):
        return self.message


class AddressNotVerified(Exception):
    pass


class FilteringError(Exception):
    def __init__(self, field, value):
        self.field = field
        self.value = value

    def __str__(self):
        return '%(value)s is not a valid value for %(field)s' % dict(field=self.field,
                                                                     value=self.value)


class BatchError(Exception):
    pass
