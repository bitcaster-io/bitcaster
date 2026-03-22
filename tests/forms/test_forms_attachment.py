from pathlib import Path

import pytest
from django.core.files.base import ContentFile

from bitcaster.forms.attachment import AttachmentForm

attachment = Path(__file__).parent / "attachment.svg"


@pytest.fixture
def data1(application):
    return ({}, {}, False)


@pytest.fixture
def data2(application):
    return (
        {"application": application.pk, "correlation_id": "abc"},
        {"document": ContentFile("pdf", "test.pdf")},
        False,
    )


@pytest.fixture
def data3(application):
    return (
        {"application": application.pk, "filename": "filename.txt", "correlation_id": "abc"},
        {"document": ContentFile("pdf", "test.pdf")},
        False,
    )


@pytest.fixture
def data4(application):
    return (
        {
            "application": application.pk,
            "mime_type": "application/pdf",
            "filename": attachment.name,
            "correlation_id": "abc",
        },
        {"document": ContentFile(attachment.read_bytes(), attachment.name)},
        True,
    )


@pytest.mark.parametrize(
    "fixture_name",
    [
        "data1",
        "data2",
        "data3",
        "data4",
    ],
)
def test_attachment_form(fixture_name, request):
    if isinstance(fixture_name, str):
        post_data, files, expected = request.getfixturevalue(fixture_name)
    else:
        post_data, files = fixture_name
    frm = AttachmentForm(post_data, files)
    assert frm.is_valid() is expected, frm.errors
