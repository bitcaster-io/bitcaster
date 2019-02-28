# -*- coding: utf-8 -*-
import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _, ngettext_lazy


class BaseValidator:
    message = _('Ensure this value is %(limit_value)s (it is %(cleaned)s).')
    code = 'limit_value'

    def __init__(self, target, limit_value, message=None):
        assert target in ['body', 'subject', 'html'], 'Target must be a Message field'
        self.limit_value = limit_value
        self.target = target
        if message:
            self.message = message

    def __call__(self, message):
        value = getattr(message, self.target)
        cleaned = self.clean(value)
        # params = {'limit_value': self.limit_value, 'show_value': cleaned, 'value': value}
        if self.compare(cleaned, self.limit_value):
            raise ValidationError({self.target: self.message % {'limit_value': self.limit_value,
                                                                'cleaned': cleaned}})

    def compare(self, a, b):
        return a is not b

    def clean(self, x):
        return x


class MaxLengthValidator(BaseValidator):
    message = ngettext_lazy(
        'Ensure this value has at most %(limit_value)d character (it has %(cleaned)d).',
        'Ensure this value has at most %(limit_value)d characters (it has %(cleaned)d).',
        'limit_value')
    code = 'max_length'

    def compare(self, a, b):
        return a > b

    def clean(self, x):
        return len(x)


class MaxBodyLengthValidator(MaxLengthValidator):
    def __init__(self, limit_value, message=None):
        super().__init__('body', limit_value, message)


class RegexFieldValidator:

    def clean(self, x):
        return x

    def __call__(self, value):
        try:
            re.compile(value)
            return True
        except Exception:
            raise ValidationError('Invalid regex')
