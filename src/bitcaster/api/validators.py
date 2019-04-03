from django.core.validators import RegexValidator


class PhoneNumberValidator(RegexValidator):
    regex = r'^\+?[1-9]\d{1,14}$'  # E.164 phone number
