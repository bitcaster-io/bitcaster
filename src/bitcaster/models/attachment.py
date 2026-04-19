from collections.abc import Iterable
from typing import override
from uuid import uuid4

from django.db import models
from django.db.models.base import ModelBase
from django.utils.translation import gettext_lazy as _

from bitcaster.models.application import Application
from bitcaster.models.mixins import BitcasterBaseModel


class Attachment(BitcasterBaseModel):
    application = models.ForeignKey(
        Application,
        verbose_name=_("Application"),
        on_delete=models.CASCADE,
        related_name="attachments",
        help_text=_("application owner of this Attachment"),
    )
    correlation_id = models.SlugField(
        verbose_name=_("Correlation ID"),
        blank=True,
        default=uuid4,
        unique=True,
        help_text=_("Unique human readable identifier for the attachment"),
    )
    filename = models.CharField(
        verbose_name=_("Filename"),
        max_length=256,
        blank=True,
        null=True,
        help_text=_("Filename to use when downloading the attachment"),
    )
    document = models.FileField(
        verbose_name=_("Document/File"), upload_to="attachments/", help_text=_("Attachment file")
    )
    mime_type = models.CharField(
        verbose_name=_("MIME Type"),
        max_length=256,
        help_text=_("MIME type of the file. It will be auto-detected if not provided"),
    )
    size = models.PositiveIntegerField(verbose_name=_("File size"), default=0, help_text=_("Attachment size in bytes"))

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
