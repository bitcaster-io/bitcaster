import logging

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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        validator = PhoneNumberValidator()
        self.validators.insert(0, validator)
