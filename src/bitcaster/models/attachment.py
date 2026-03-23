from collections.abc import Iterable
from typing import override
from uuid import uuid4

from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import gettext_lazy as _

from bitcaster.models.application import Application
from bitcaster.models.mixins import BitcasterBaseModel


class Attachment(BitcasterBaseModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="attachments")
    correlation_id = models.SlugField(
        default=uuid4,
        unique=True,
        blank=True,
        verbose_name=_("Correlation ID"),
        help_text=_("Unique human readable identifier for the attachment"),
    )
    filename = models.CharField(
        max_length=256,
        null=True,
        blank=True,
        verbose_name=_("Filename"),
        help_text=_("Filename to use when downloading the attachment"),
    )
    document = models.FileField(upload_to="attachments/", help_text=_("Attachment file"))
    mime_type = models.CharField(
        max_length=256, help_text=_("MIME type of the file. It will be auto-detected if not provided")
    )
    size = models.PositiveIntegerField(default=0, help_text=_("Attachment size in bytes"))

    @override
    def __str__(self) -> str:
        return f"{self.filename} ({self.correlation_id})"

    @override
    def save(
        self,
        *,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: str | None = None,
        update_fields: Iterable[str] | None = None,
    ) -> None:
        self.size = self.document.size
        if not self.correlation_id:
            self.correlation_id = uuid4().hex
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    @override
    def natural_key(self) -> tuple[str, ...]:
        return (str(self.correlation_id), *self.application.natural_key())
