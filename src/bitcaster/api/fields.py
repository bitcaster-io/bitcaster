import logging

from django.utils.translation import gettext_lazy as _
from rest_framework.fields import CharField, ChoiceField

from bitcaster.api.validators import PhoneNumberValidator
from bitcaster.plugins.validators import RegexFieldValidator

logger = logging.getLogger(__name__)


class PasswordField(CharField):
    pass


class EventField(ChoiceField):
    pass


class RegexField(CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        validator = RegexFieldValidator()
        self.validators.append(validator)


class PhoneNumberField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid phone number.')
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        validator = PhoneNumberValidator(message=self.error_messages['invalid'])
        self.validators.append(validator)
