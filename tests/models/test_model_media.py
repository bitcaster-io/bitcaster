import factory
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
