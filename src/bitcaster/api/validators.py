from django.core.validators import RegexValidator


class PhoneNumberValidator(RegexValidator):
    regex = r'^\+\d{5,}'
