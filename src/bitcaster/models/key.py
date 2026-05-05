from typing import Any

import logging
from urllib.parse import urlsplit, urlunsplit

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.crypto import RANDOM_STRING_CHARS, get_random_string
from django.utils.translation import gettext_lazy as _

from bitcaster.auth.constants import Grant
from bitcaster.utils.http import absolute_reverse

from .mixins import BitcasterBaseModel, Scoped3Mixin, ScopedManager
from .user import User

logger = logging.getLogger(__name__)

TOKEN_CHARS = f"{RANDOM_STRING_CHARS}-_~."


def make_token() -> str:
    return get_random_string(96, TOKEN_CHARS)


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
        return super().formfield(**defaults)  # type: ignore[return-value, arg-type]


class ApiKeyManager(ScopedManager["ApiKey"]):
    def get_by_natural_key(self, name: "str", user: "str", *args: Any) -> "ApiKey":
        return self.get(name=name, user__username=user)


class ApiKey(Scoped3Mixin, BitcasterBaseModel):
    name = models.CharField(
        verbose_name=_("Name"),
        max_length=255,
        db_index=True,
        db_collation="case_insensitive",
        help_text=_("name of his key"),
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="keys",
        help_text=_("user responsible of this key"),
    )
    key = models.CharField(
        verbose_name=_("Token"), max_length=255, default=make_token, unique=True, help_text=_("api key")
    )
    grants = ChoiceArrayField(
        models.CharField(max_length=255, choices=Grant.choices),
        verbose_name=_("Grants"),
        blank=True,
        null=True,
        help_text=_("grants for this key"),
    )
    environments = ArrayField(
        models.CharField(max_length=20, blank=True, null=True),
        verbose_name=_("Environments"),
        blank=True,
        null=True,
        help_text=_("Limit validity to these environments. If empty the key will be valid for any environment"),
    )
    objects = ApiKeyManager()

    class Meta:
        ordering = ("name",)
        unique_together = (("name", "user"),)
        verbose_name = _("Api Key")
        verbose_name_plural = _("Api Keys")

    def get_bae(self) -> str:
        password = self.key
        if self.project:
            url = absolute_reverse("api:project-detail", args=[self.organization.slug, self.project.slug])
        else:
            url = absolute_reverse("api:org", args=[self.organization.slug])

        url_parts = urlsplit(url)
        netloc = f"{password}@{url_parts.hostname}"
        if url_parts.port:
            netloc += f":{url_parts.port}"
        return urlunsplit((url_parts.scheme, netloc, url_parts.path, url_parts.query, url_parts.fragment))

    def natural_key(self) -> tuple[str, ...]:
        return self.name, self.user.username

    def __str__(self) -> str:
        return self.name
