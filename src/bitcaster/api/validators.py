from django.core.validators import RegexValidator
from django.utils.translation import gettext as _


class PhoneNumberValidator(RegexValidator):
    regex = r'^\+?[1-9]\d{1,14}$'  # E.164 phone number
    message = _('Please insert phone number using E.164 format. (+<country_code><number>')
