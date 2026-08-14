from typing import Any

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from bitcaster.auth.constants import Grant

from .key import make_token
from .mixins import BitcasterBaseModel, Scoped3Mixin
from .user import User


class ClientToken(Scoped3Mixin, BitcasterBaseModel):
    token = models.CharField(
        verbose_name=_("Token"), max_length=255, default=make_token, unique=True, help_text=_("client token")
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="client_tokens",
        help_text=_("user that owns this token"),
    )
    parent = models.ForeignKey(
        "ApiKey",
        verbose_name=_("Parent key"),
        on_delete=models.CASCADE,
        related_name="client_tokens",
        blank=True,
        null=True,
        help_text=_("api key that minted this token"),
    )
    event = models.ForeignKey(
        "Event",
        verbose_name=_("Event"),
        on_delete=models.CASCADE,
        related_name="client_tokens",
        blank=True,
        null=True,
        help_text=_("if set the token can only trigger this event"),
    )
    environments = ArrayField(
        models.CharField(max_length=20, blank=True, null=True),
        verbose_name=_("Environments"),
        blank=True,
        null=True,
        help_text=_("Limit validity to these environments. If empty the token will be valid for any environment"),
    )
    allowed_origins = ArrayField(
        models.CharField(max_length=255),
        verbose_name=_("Allowed origins"),
        help_text=_("Origins allowed to use this token. Requests without a matching Origin are rejected"),
    )
    expires_at = models.DateTimeField(verbose_name=_("Expires at"), help_text=_("Token expiration date"))
    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_("If unchecked the token is revoked and cannot be used"),
    )
    last_used_at = models.DateTimeField(
        verbose_name=_("Last used at"),
        blank=True,
        null=True,
        editable=False,
        help_text=_("Timestamp of the last successful authentication"),
    )

    class Meta:
        ordering = ("-created",)
        verbose_name = _("Client Token")
        verbose_name_plural = _("Client Tokens")

    @property
    def grants(self) -> list[str]:
        return [Grant.WEB_TRIGGER]

    def is_web(self) -> bool:
        return True

    def clean(self) -> None:
        super().clean()
        if not self.expires_at:
            raise ValidationError({"expires_at": _("Client tokens must have an expiration date")})
        if not self.application:
            raise ValidationError({"application": _("Client tokens must be scoped to an application")})
        if self.event and self.event.application_id != self.application_id:
            raise ValidationError({"event": _("Event must belong to the application")})
        if not self.allowed_origins:
            raise ValidationError({"allowed_origins": _("Client tokens require at least one allowed origin")})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean(exclude=["token"])
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.application} {self.token[:8]}"

    def natural_key(self) -> tuple[str, ...]:
        return (self.token,)
