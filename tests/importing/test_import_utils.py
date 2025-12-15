import pytest

from bitcaster.importing.utils import get_column_mapping, parse_kv


@pytest.mark.parametrize(
    "fields,expected",
    [
        (["email"], {"email": "email"}),
        (["Email "], {"email": "Email "}),
        (["first Name"], {"first_name": "first Name"}),
    ],
)
def test_get_column_mapping(fields, expected) -> None:
    assert get_column_mapping(fields) == expected


@pytest.mark.parametrize("value,expected", [("a=1", {"a": 1}), ("a", {})])
def test_parse_kv(value, expected) -> None:
    assert parse_kv(value) == expected
