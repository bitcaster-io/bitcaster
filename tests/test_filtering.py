from typing import TYPE_CHECKING

import pytest

from django.core.exceptions import ValidationError

from bitcaster.models import User
from bitcaster.utils.filtering import FilterManager, validate_filters, validate_lookups, validate_schema

if TYPE_CHECKING:
    from bitcaster.types.filtering import QuerysetFilter


@pytest.mark.parametrize(
    "includes, expected",
    [
        ([], 2),
        ({}, 2),
        # AND
        ({"username": "superuser@example.com"}, 1),
        ({"username__in": ["superuser@example.com"]}, 1),
        ([{"username": "superuser@example.com"}], 1),
        ([{"username": "user@example.com"}], 1),
        ([{"username": "superuser@example.com", "is_superuser": True}], 1),
        # OR
        ([{"username": "superuser@example.com"}, {"username": "user@example.com"}], 2),
        ([{"username": "superuser@example.com", "is_superuser": False}], 0),
        # AND of ORs:
        ([[{"username": "superuser@example.com"}], [{"username": "user@example.com"}]], 0),
        ([[{"username": "superuser@example.com"}, {"email": "superuser@example.com"}], [{"is_superuser": True}]], 1),
        ([[{"username": "superuser@example.com"}, {"username": "user@example.com"}], [{"is_superuser": False}]], 1),
    ],
)
def test_filtering_include(superuser: User, user: User, includes, expected) -> None:
    manager = FilterManager(User.objects, {"include": includes, "exclude": []})
    result = len(manager.filter().values_list("pk", flat=True))
    assert result == expected, f"{result} != {expected} using {includes}"


@pytest.mark.parametrize(
    "excludes, expected",
    [
        ([], 2),
        ({}, 2),
        # AND
        ({"username": "superuser@example.com"}, 1),
        ({"username__in": ["superuser@example.com"]}, 1),
        ([{"username": "superuser@example.com"}], 1),
        ([{"username": "user@example.com"}], 1),
        ([{"username": "superuser@example.com", "is_superuser": True}], 1),
        # OR
        ([{"username": "superuser@example.com"}, {"username": "user@example.com"}], 0),
        ([{"username": "superuser@example.com", "is_superuser": False}], 2),
        ([[{"username": "superuser@example.com"}], [{"username": "user@example.com"}]], 2),
        # AND of ORs:
        ([[{"username": "superuser@example.com"}, {"email": "superuser@example.com"}], [{"is_superuser": True}]], 1),
        # AND of ORs:
        ([[{"username": "superuser@example.com"}, {"username": "user@example.com"}], [{"is_superuser": False}]], 1),
    ],
)
def test_filtering_exclude(superuser: User, user: User, excludes, expected) -> None:
    manager = FilterManager(User.objects, {"exclude": excludes, "include": []})
    result = len(manager.filter().values_list("pk", flat=True))
    assert result == expected, f"{result} != {expected} using {excludes}"


@pytest.mark.parametrize(
    "excludes, expected",
    [
        # AND
        ({"username": "superuser@example.com"}, True),
        ([{"username": "superuser@example.com"}], True),
        ([{"username": "user@example.com"}], True),
        ([{"username": "superuser@example.com", "is_superuser": True}], True),
        # OR
        ([{"username": "superuser@example.com"}, {"username": "user@example.com"}], True),
        ([{"username": "superuser@example.com", "is_superuser": False}], True),
        ([[{"username": "superuser@example.com"}], [{"username": "user@example.com"}]], True),
        # AND of ORs:
        ([[{"username": "superuser@example.com"}, {"email": "superuser@example.com"}], [{"is_superuser": True}]], True),
        # AND of ORs:
        ([[{"username": "superuser@example.com"}, {"username": "user@example.com"}], [{"is_superuser": False}]], True),
    ],
)
def test_validate(excludes, expected) -> None:
    filters = {"exclude": excludes, "include": []}
    e = None
    try:
        validate_schema(filters)
        success = True
    except ValidationError as ex:
        e = ex
        success = False
    assert success == expected, f"{e}: {filters}"


@pytest.mark.parametrize(
    "excludes, expected",
    [
        # AND
        ({"username": "superuser@example.com"}, True),
        ({"aaa": "superuser@example.com"}, False),
        ({"username__ERROR": "superuser@example.com"}, False),
        ([{"username": "superuser@example.com"}], True),
        ([{"username": "user@example.com"}], True),
        ([{"username": "superuser@example.com", "is_superuser": True}], True),
        # OR
        ([{"username": "superuser@example.com"}, {"username": "user@example.com"}], True),
        ([{"username": "superuser@example.com", "is_superuser": False}], True),
        ([[{"username": "superuser@example.com"}], [{"username": "user@example.com"}]], True),
        # AND of ORs:
        ([[{"username": "superuser@example.com"}, {"email": "superuser@example.com"}], [{"is_superuser": True}]], True),
        # AND of ORs:
        ([[{"username": "superuser@example.com"}, {"username": "user@example.com"}], [{"is_superuser": False}]], True),
    ],
)
def test_validate_filters(excludes, expected) -> None:
    filters: "QuerysetFilter" = {"exclude": excludes, "include": []}
    e = None
    try:
        validate_filters(User.objects, filters)
        success = True
    except ValidationError as ex:
        e = ex
        success = False
    assert success == expected, f"{e}: {filters}"


@pytest.mark.parametrize(
    "excludes, expected",
    [
        # AND
        ({"password": "22"}, False),
        ({"username": "superuser@example.com", "password": "22"}, False),
        ([[{"username": "superuser@example.com"}], [{"password": "user@example.com"}]], False),
        ({"username": "superuser@example.com"}, True),
    ],
)
def test_validate_lookups(excludes, expected) -> None:
    filters: "QuerysetFilter" = {"exclude": excludes, "include": []}
    e = None
    try:
        validate_lookups(User, filters)
        success = True
    except ValidationError as ex:
        e = ex
        success = False
    assert success == expected, f"{e}: {filters}"


@pytest.mark.parametrize(
    "value, expected",
    [
        ({"include": [], "exclude": []}, True),
        ({}, False),
        ([], False),
        (22, False),
    ],
)
def test_validate_schema(value, expected) -> None:
    e = None
    try:
        validate_schema(value)
        success = True
    except ValidationError as ex:
        e = ex
        success = False
    assert success == expected, f"{e}: {value}"
