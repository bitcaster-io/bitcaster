import logging
from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.forms import CharField, ChoiceField

from bitcaster.models import Channel

logger = logging.getLogger(__name__)


def clean(v: str) -> str:
    return v.replace(r"\n", "").strip()


# class FlagField(TypedChoiceField):
#     def __init__(self, *, coerce=lambda val: val, empty_value="", **kwargs):
#         self.empty_value = empty_value
#         super().__init__(**kwargs)
#         self.coerce = lambda v: sum(map(int, v))
#
#     def clean(self, value):
#         # value = super().clean(value)
#         return self._coerce(value)
#
#
# class CheckboxSelectFlags(CheckboxSelectMultiple):
#     def format_value(self, value):
#         return [x for x in "{0:03b}".format(value)]
#
#     def value_from_datadict(self, data, files, name):
#         getter = data.get
#         if self.allow_multiple_selected:
#             try:
#                 getter = data.getlist
#             except AttributeError:
#                 pass
#         return getter(name)


class EmailsFormField(CharField):
    widget = forms.Textarea

    def clean(self, value: Any) -> Any:
        if not value:
            return ""
        errors = []
        validate_email = EmailValidator("%(value)s is not a valid email")
        try:
            emails = value.split(",")
            for email in emails:
                try:
                    validate_email(email.strip())
                except ValidationError as e:
                    errors.append(e)
        except Exception as e:
            raise ValidationError(str(e))
        if errors:
            raise ValidationError(errors)
        return value


class EmailChannel(ChoiceField):
    def __init__(self, **kwargs: Any) -> None:
        ret = [["", "None"]]
        for c in Channel.objects.values("pk", "name"):
            ret.append([c["pk"], c["name"]])
        kwargs["choices"] = ret
        super().__init__(**kwargs)
