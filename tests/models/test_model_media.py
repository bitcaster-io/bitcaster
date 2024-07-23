from typing import Any
from unittest import mock

import factory
import pytest
from django.core.files.base import ContentFile
from django.db.models.fields.files import ImageFieldFile

from bitcaster.models import Application


@pytest.mark.parametrize("format,mime", [("ICO", "image/vnd.microsoft.icon"), ("JPEG", "image/jpeg")])
def test_mediafile_success(application: "Application", format: str, mime: str) -> None:
    from testutils.factories import MediaFile, MediaFileFactory

    m: MediaFile = MediaFileFactory.build(
        application=application,
        image=ContentFile(factory.django.ImageField()._make_data({"format": format}), "logo.%s" % format.lower()),
    )
    m.save()
    assert m.image
    assert m.mime_type == mime


def test_mediafile_missing(application: "Application") -> None:
    from testutils.factories import MediaFile, MediaFileFactory

    m: MediaFile = MediaFileFactory.build(application=application, image=None)
    m.save()
    assert not m.image
    assert not m.mime_type


@pytest.mark.parametrize("args", [{}, {"application": None}, {"project": None, "application": None}])
def test_natural_key(args: dict[str, Any]) -> None:
    from testutils.factories import MediaFile, MediaFileFactory

    media = MediaFileFactory(name="media", image=None, **args)
    assert MediaFile.objects.get_by_natural_key(*media.natural_key()) == media, media.natural_key()


@pytest.mark.parametrize("size", ["size", ""])
@pytest.mark.parametrize("mime", ["mime_type", ""])
def test_imagefield(application: "Application", mime: str, size: str) -> None:
    from testutils.factories import MediaFile, MediaFileFactory

    f = MediaFile.image.field
    with mock.patch.object(f, "mime_field", mime):
        with mock.patch.object(f, "size_field", size):
            media = MediaFileFactory.build(
                application=application,
                image=ContentFile(factory.django.ImageField()._make_data({"width": 64, "format": "ICO"}), "logo.ico"),
            )
            media.save()
            assert media.pk
            media.image.field.update_dimension_fields(media, force=True)
            media.image.field.update_dimension_fields(media, force=True)


def test_imagefield_cache(application: "Application") -> None:
    from testutils.factories import MediaFile, MediaFileFactory

    f = MediaFile.image.field
    with mock.patch.object(f, "mime_field", "mime_type"):
        with mock.patch.object(f, "size_field", "size"):
            media = MediaFileFactory.build(
                application=application,
                image=ContentFile(factory.django.ImageField()._make_data({"width": 64, "format": "ICO"}), "logo.ico"),
            )
            delattr(media, "_mime_cache")
            media.image.field.update_dimension_fields(media, force=True)
            media.image.field.update_dimension_fields(media, force=True)


def test_imagefield_closed_file(application: "Application") -> None:
    from testutils.factories import MediaFileFactory

    with mock.patch.object(ImageFieldFile, "closed", True):
        media = MediaFileFactory.build(
            application=application,
            image=ContentFile(factory.django.ImageField()._make_data({"width": 64, "format": "ICO"}), "logo.ico"),
        )
        media.image.field.update_dimension_fields(media, force=True)
