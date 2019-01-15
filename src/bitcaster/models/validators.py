from django.core import validators
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


class NameValidator(validators.RegexValidator):
    regex = r'^[\w -]+$'
    message = _('Enter a valid name.')


@deconstructible
class ListValidator:
    default_message = '{value} is a forbidden {param}.'
    default_param = 'name'
    code = 'E001'

    def __init__(self, values, param=None, message=None):
        self.values = values
        self.message = message or self.default_message
        self.param = param or self.default_param

    def __call__(self, value):
        if value in self.values:
            raise ValidationError(self.message.format(value=value,
                                                      param=self.param), code=self.code)
