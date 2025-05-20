from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from phonenumbers import NumberParseException, parse


def is_phonenumber(value: str) -> bool:
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
