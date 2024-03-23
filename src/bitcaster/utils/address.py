import phonenumbers
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from phonenumbers import NumberParseException, parse


def is_phonenumber(value: str) -> bool:
    #
    try:
        parse(value)
        return True
    except (NumberParseException, Exception):
        return False


def is_email(value: str) -> bool:
    try:
        EmailValidator()(str(value))
        return True
    except ValidationError:
        return False


def format_phone(value: str) -> str:
    return phonenumbers.format_number(phonenumbers.parse(value), phonenumbers.PhoneNumberFormat.INTERNATIONAL)


def clean_format_phone(value: str) -> str:
    # TODO: Validate number using https://lookups.twilio.com/v1/PhoneNumbers/+39339229950.
    #  raise ValidationError if any issue
    return phonenumbers.format_number(phonenumbers.parse(value), phonenumbers.PhoneNumberFormat.E164)
