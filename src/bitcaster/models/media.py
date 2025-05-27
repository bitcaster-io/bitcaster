from typing import TYPE_CHECKING, Any

import magic
from django.core.files.storage import storages
from django.db import models
from django.db.models.fields.files import ImageFieldFile

from bitcaster.models.mixins import (
    BitcasterBaseModel,
    Scoped3Mixin,
    ScopedManager,
    SlugMixin,
)

if TYPE_CHECKING:
    from bitcaster.types.django import AnyModel

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


class ImageFieldWithExtra(models.ImageField):
    def __init__(
        self,
        verbose_name: str | None = None,
        name: str | None = None,
        width_field: str | None = None,
        height_field: str | None = None,
        mime_field: str | None = None,
        size_field: str | None = None,
        **kwargs: Any,
    ):
        self.mime_field = mime_field
        self.size_field = size_field
        super().__init__(verbose_name, name, width_field, height_field, **kwargs)

    def _get_mime(self, instance: "AnyModel", file: ImageFieldFile) -> str | None:
        if not hasattr(instance, "_mime_cache"):
            file_pos = None
            close = file.closed
            if not close:
                file_pos = file.tell()
            else:
                file.open()
            try:
                mime_type = mime.from_buffer(file.file.read())
                instance._mime_cache = mime_type
            finally:
                if close:
                    file.close()
                else:
                    file.seek(file_pos)
        return instance._mime_cache

    def update_dimension_fields(self, instance: "AnyModel", force: bool = False, *args: "Any", **kwargs: "Any") -> None:
        super().update_dimension_fields(instance, force, *args, **kwargs)
        if self.mime_field or self.size_field:
            file: ImageFieldFile = getattr(instance, self.attname)
            if not file and not force:
                return
            if self.mime_field:
                mime_type = self._get_mime(instance, file)
                setattr(instance, self.mime_field, mime_type)

            if self.size_field:
                setattr(instance, self.size_field, file.size)


class MediaFile(Scoped3Mixin, SlugMixin, BitcasterBaseModel):
    image = ImageFieldWithExtra(
        storage=storages["mediafiles"],
        width_field="width",
        height_field="height",
        size_field="size",
        mime_field="mime_type",
    )
    size = models.PositiveIntegerField(blank=True, default=0, null=True)
    width = models.PositiveIntegerField(blank=True, default=0, null=True)
    height = models.PositiveIntegerField(blank=True, default=0, null=True)

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
        if self.project:
            return self.name, None, *self.project.natural_key()
        return self.name, None, None, *self.organization.natural_key()

    #
    # def save(
    #     self,
    #     force_insert: bool | tuple[ModelBase, ...] = False,
    #     force_update: bool = False,
    #     using: Optional[str] = None,
    #     update_fields: Optional[Iterable[str]] = None,
    # ) -> None:
    #     super().save(force_insert, force_update, using, update_fields)
    #
