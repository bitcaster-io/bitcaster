import logging
from typing import Any

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.crypto import RANDOM_STRING_CHARS, get_random_string
from django.utils.translation import gettext_lazy as _

from bitcaster.auth.constants import Grant

from .org import Application
from .user import User

logger = logging.getLogger(__name__)

TOKEN_CHARS = f"{RANDOM_STRING_CHARS}-#@^*_+~;<>,."


def make_token() -> str:
    return get_random_string(250, TOKEN_CHARS)


class _TypedMultipleChoiceField(forms.TypedMultipleChoiceField):
    widget = CheckboxSelectMultiple

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.pop("base_field", None)
        kwargs.pop("max_length", None)
        super().__init__(*args, **kwargs)


class ChoiceArrayField(ArrayField):  # type: ignore[type-arg]

    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> forms.Field:
        defaults = {
            "form_class": _TypedMultipleChoiceField,
            "choices": self.base_field.choices,
            "coerce": self.base_field.to_python,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)  # type: ignore[arg-type]


class ApiKey(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=255, db_collation="case_insensitive")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(verbose_name=_("Token"), unique=True, default=make_token)
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    grants = ChoiceArrayField(models.CharField(max_length=255, choices=Grant.choices), null=True, blank=True)

    class Meta:
        ordering = ("name",)
        unique_together = (("name", "user"),)
