from pathlib import Path

import pytest

from django.core.files.base import ContentFile

from bitcaster.forms.media import MediaFileForm

attachment = Path(__file__).parent / "attachment.png"


@pytest.fixture
def data1(application):
    return ({}, {}, False)


@pytest.fixture
def data2(application):
    return (
        {"name": "name", "slug": "slug"},
        {"image": ContentFile(b"pdf", "test.pdf")},
        False,
    )


@pytest.fixture
def data3(application):
    return (
        {"name": "name", "slug": "slug"},
        {"image": ContentFile(b"", "test.pdf")},
        False,
    )


@pytest.fixture
def data4(application):
    return (
        {
            "name": "name",
            "slug": "slug",
        },
        {"image": ContentFile(attachment.read_bytes(), attachment.name)},
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
    frm = MediaFileForm(post_data, files)
    assert frm.is_valid() is expected, frm.errors
