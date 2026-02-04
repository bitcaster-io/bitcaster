import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from testutils.factories import AttachmentFactory


@pytest.fixture
def text_file():
    return SimpleUploadedFile("test.txt", b"Test text file", content_type="text/plain")


@pytest.fixture
def text_attachment(text_file):
    return AttachmentFactory(document=text_file)


def test_generates_correlation_id_mime_type_and_size_on_creation(text_attachment):
    assert text_attachment.correlation_id
    assert text_attachment.mime_type == "text/plain"
    assert text_attachment.size == len(b"Test text file")
