from typing import Any
from unittest import mock

import pytest
from django.core.files import File
from testutils.helpers import get_resource

from bitcaster.importing.members import import_members_csv, process_csv_line
from bitcaster.importing.utils import get_column_mapping


@pytest.mark.parametrize(
    "line, expected",
    [
        (
            {"email": "a1@b.com", "first_name": "test"},
            {"email": "a1@b.com", "first_name": "test", "custom_fields": {}, "username": "a1@b.com"},
        ),
        ({"email": "a2@b.com", "invalid": "abc"}, NotImplementedError),
        (
            {"email": "a3@b.com", "custom__abc": "test"},
            {"email": "a3@b.com", "custom_fields": {"abc": "test"}, "username": "a3@b.com"},
        ),
        (
            {"email": "a4@b.com", "custom__abc[]": "test1, test2"},
            {"email": "a4@b.com", "custom_fields": {"abc": ["test1", "test2"]}, "username": "a4@b.com"},
        ),
        (
            {"email": "a5@b.com", "custom__abc{}": "key1=value1"},
            {"email": "a5@b.com", "custom_fields": {"abc": {"key1": "value1"}}, "username": "a5@b.com"},
        ),
        (
            {"email": "a6@b.com", "custom__abc{}": "key1=value1,key2=value2"},
            {
                "email": "a6@b.com",
                "custom_fields": {"abc": {"key1": "value1", "key2": "value2"}},
                "username": "a6@b.com",
            },
        ),
        ({"email": "a7@b.com", "custom__abc{}": "key1=value1,key2=[]"}, NotImplementedError),
        (
            {"email": "a8@b.com", "custom__abc{}": 'key1=value1,key2="value 2"'},
            {
                "email": "a8@b.com",
                "custom_fields": {"abc": {"key1": "value1", "key2": "value 2"}},
                "username": "a8@b.com",
            },
        ),
        (
            {"email": "a9@b.com", "first Name": "John"},
            {"email": "a9@b.com", "custom_fields": {}, "username": "a9@b.com", "first_name": "John"},
        ),
    ],
)
def test_process_csv_line(line: dict[str, Any], expected) -> None:
    mapping = get_column_mapping(line.keys())
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            process_csv_line(line, mapping)
    else:
        result = process_csv_line(line, mapping)
        assert result == expected


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("members_ok.csv", (2, 3)),
        ("members1.csv", NotImplementedError),
        ("members_no_email.csv", (0, 3)),
        ("members_clean_fields.csv", (2, 2)),
    ],
)
def test_import_csv(filename: str, expected) -> None:
    data = File(get_resource(f"data/{filename}").open("rb"))

    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            import_members_csv(data)
    else:
        result = import_members_csv(data)
        assert result == expected


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            [b'Email,"First Name"\n', b"a@b.com,Name1\n", b'a@b.com,"Name #1"\n'],
            {"email": "a@b.com", "first_name": "Name #1"},
        ),
    ],
)
def test_import_csv_columns_cleaning(data: str, expected) -> None:
    def mocked(d, *, ignore_conflicts=True):
        assert d[0].email == expected["email"]
        return d

    with mock.patch("bitcaster.models.user.Member.objects.bulk_create", mocked):
        import_members_csv(data)
