from typing import Iterable, Optional

import magic
from django.core.files.storage import Storage, storages
from django.db import models
from django.db.models.base import ModelBase

from bitcaster.models.mixins import ScopedMixin, SlugMixin

mime = magic.Magic(mime=True)


class MediaFile(ScopedMixin, SlugMixin, models.Model):
    image = models.ImageField(storage=storages["mediafiles"], width_field="width", height_field="height")
    size = models.PositiveIntegerField(blank=True, default=0)
    width = models.PositiveIntegerField(blank=True, default=0)
    height = models.PositiveIntegerField(blank=True, default=0)

    mime_type = models.CharField(max_length=100, blank=True, default="")
    file_type = models.CharField(max_length=100, blank=True, default="")

    class Meta:
        unique_together = (
            ("slug", "organization", "project", "application"),
            ("slug", "organization", "project"),
            ("slug", "organization"),
        )

    def save(
        self,
        force_insert: bool | tuple[ModelBase, ...] = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        if not self.mime_type and not self.pk:
            storage: Storage = storages["mediafiles"]
            if self.image and storage.exists(self.image.name):
                self.mime_type = mime.from_buffer(storage.open(self.image.name).read())
                self.size = storage.size(self.image.name)

        super().save(force_insert, force_update, using, update_fields)
