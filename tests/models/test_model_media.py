import factory
import pytest
from django.core.files.base import ContentFile


def test_mediafile(application):
    from testutils.factories import MediaFile, MediaFileFactory

    m: MediaFile = MediaFileFactory.build(
        application=application,
        image=ContentFile(factory.django.ImageField()._make_data({"width": 1024, "height": 768}), "logo.jpeg"),
    )
    m.save()
    assert m.image
    assert m.mime_type == "image/jpeg"


def test_mediafile_missing(application):
    from testutils.factories import MediaFile, MediaFileFactory

    m: MediaFile = MediaFileFactory.build(
        application=application,
        image=None,
    )
    m.save()
    assert not m.image
    assert not m.mime_type


@pytest.mark.parametrize("args", [{}, {"application": None}, {"project": None, "application": None}])
def test_natural_key(args):
    from testutils.factories import MediaFile, MediaFileFactory

    media = MediaFileFactory(name="media", image=None, **args)
    assert MediaFile.objects.get_by_natural_key(*media.natural_key()) == media, media.natural_key()
