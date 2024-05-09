from typing import Iterable, Optional

import magic
from django.core.files.storage import Storage, storages
from django.db import models
from django.db.models.base import ModelBase

from bitcaster.models.mixins import (
    BitcasterBaseModel,
    ScopedManager,
    ScopedMixin,
    SlugMixin,
)

mime = magic.Magic(mime=True)


class MediaFileManager(ScopedManager["MediaFile"]):
    def get_by_natural_key(self, name: str, app: str, prj: str, org: str) -> "MediaFile":
        filters: dict[str, str | None] = {}
        if app:
            filters["application__slug"] = app
        else:
            filters["application"] = None

        if prj:
            filters["project__slug"] = prj
        else:
            filters["project"] = None

        return self.get(name=name, organization__slug=org, **filters)


class MediaFile(ScopedMixin, SlugMixin, BitcasterBaseModel):
    image = models.ImageField(storage=storages["mediafiles"], width_field="width", height_field="height")
    size = models.PositiveIntegerField(blank=True, default=0)
    width = models.PositiveIntegerField(blank=True, default=0)
    height = models.PositiveIntegerField(blank=True, default=0)

    mime_type = models.CharField(max_length=100, blank=True, default="")
    file_type = models.CharField(max_length=100, blank=True, default="")

    objects = MediaFileManager()

    class Meta:
        unique_together = (
            ("slug", "organization", "project", "application"),
            ("slug", "organization", "project"),
            ("slug", "organization"),
        )

    def natural_key(self) -> tuple[str | None, ...]:
        if self.application:
            return self.name, *self.application.natural_key()
        elif self.project:
            return self.name, None, *self.project.natural_key()
        else:
            return self.name, None, None, *self.organization.natural_key()

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
