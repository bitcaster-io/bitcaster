# -*- coding: utf-8 -*-
import logging

from django.utils.translation import gettext as _
from rest_framework.fields import CharField

from mercury.api.validators import PhoneNumberValidator

logger = logging.getLogger(__name__)


class PhoneNumberField(CharField):
    default_error_messages = {
        'invalid': _('Enter a valid phone number.')
    }

    def __init__(self, **kwargs):
        super(PhoneNumberField, self).__init__(**kwargs)
        validator = PhoneNumberValidator(message=self.error_messages['invalid'])
        self.validators.append(validator)
