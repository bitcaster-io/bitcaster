from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError
from django.db.models import Q

from bitcaster.models import User
from bitcaster.utils.filtering import (
    FilterManager,
    normalize_groups,
    parse_filter_clause,
    validate_filters,
    validate_lookups,
    validate_schema,
)


# Tests for validate_schema
@pytest.mark.parametrize(
    "data",
    [
        {"include": {"username": "test"}, "exclude": {}},
        {"include": [{"username": "test"}], "exclude": []},
        {"include": [[{"username": "test"}]], "exclude": []},
        {"include": [], "exclude": []},
        {"include": {}, "exclude": {}},
        {"include": {"username__in": ["a", "b"]}, "exclude": []},
    ],
)
def test_validate_schema_valid(data):
    validate_schema(data)


@pytest.mark.parametrize(
    "data",
    [
        {"include": "string", "exclude": []},  # Invalid type for include
        {"include": [], "exclude": "string"},  # Invalid type for exclude
        {"include": [{"username": {"nested": "dict"}}], "exclude": []},  # Invalid value type
        {"extra_field": "value", "include": [], "exclude": []},  # Additional properties
        {"include": []},  # Missing 'exclude'
    ],
)
def test_validate_schema_invalid(data):
    with pytest.raises(ValidationError):
        validate_schema(data)


# Tests for normalize_groups
@pytest.mark.parametrize(
    "data, expected",
    [
        ({"a": 1}, [[{"a": 1}]]),
        ([{"a": 1}], [[{"a": 1}]]),
        ([[{"a": 1}]], [[{"a": 1}]]),
        ([], []),
    ],
)
def test_normalize_groups(data, expected):
    assert normalize_groups(data) == expected


@pytest.mark.parametrize(
    "data",
    [
        "string",  # Not a dict or list
        [1, 2],  # List of non-dicts
        [{"a": 1}, 2],  # Mixed list
        [[{"a": 1}], [2]],  # List of lists with invalid inner content
    ],
)
def test_normalize_groups_invalid(data):
    with pytest.raises(TypeError):
        normalize_groups(data)


# Tests for parse_filter_clause
def test_parse_filter_clause_simple():
    q = parse_filter_clause({"username": "test"})
    assert isinstance(q, Q)
    assert str(q) == str(Q(username="test"))


def test_parse_filter_clause_or():
    q = parse_filter_clause([{"username": "test1"}, {"username": "test2"}])
    assert isinstance(q, Q)
    assert str(q) == str(Q(username="test1") | Q(username="test2"))


def test_parse_filter_clause_and():
    q = parse_filter_clause([[{"username": "test"}], [{"is_active": True}]])
    assert isinstance(q, Q)
    assert str(q) == str(Q(username="test") & Q(is_active=True))


# Tests for FilterManager
@pytest.mark.django_db
def test_filter_manager_include():
    User.objects.create(username="test1", is_active=True)
    User.objects.create(username="test2", is_active=False)
    filter_spec = {"include": {"is_active": True}, "exclude": {}}
    fm = FilterManager(User.objects.all(), filter_spec)
    assert fm.filter().count() == 1
    assert fm.filter().first().username == "test1"


@pytest.mark.django_db
def test_filter_manager_exclude():
    User.objects.create(username="test1")
    User.objects.create(username="test2")
    filter_spec = {"include": {}, "exclude": {"username": "test2"}}
    fm = FilterManager(User.objects.all(), filter_spec)
    assert fm.filter().count() == 1
    assert fm.filter().first().username == "test1"


@pytest.mark.django_db
def test_filter_manager_complex():
    User.objects.create(username="test1", is_active=True)
    User.objects.create(username="test2", is_active=True)
    User.objects.create(username="admin", is_active=True)

    filter_spec = {
        "include": {"is_active": True},
        "exclude": {"username": "admin"},
    }

    fm = FilterManager(User.objects.all(), filter_spec)
    result = fm.filter()

    assert result.count() == 2
    assert set(result.values_list("username", flat=True)) == {"test1", "test2"}


@pytest.mark.django_db
def test_filter_manager_no_spec():
    User.objects.create(username="test1")
    fm = FilterManager(User.objects.all(), None)
    assert fm.filter().count() == 1


# Tests for validate_lookups
@pytest.mark.django_db
def test_validate_lookups_invalid():
    filter_spec = {"include": {"password": "test"}, "exclude": {}}
    with pytest.raises(ValidationError, match="Unauthorised lookup: 'password'"):
        validate_lookups(User, filter_spec)


@pytest.mark.django_db
def test_validate_lookups_valid():
    filter_spec = {"include": {"username": "test"}, "exclude": {}}
    validate_lookups(User, filter_spec)  # Should not raise


@pytest.mark.django_db
def test_validate_lookups_empty_filter():
    filter_spec = {"include": {}, "exclude": {}}
    validate_lookups(User, filter_spec)  # Should not raise


@pytest.mark.django_db
def test_validate_lookups_invalid_entry():
    q = Q(username="test")
    q.children = ["invalid"]
    with patch("bitcaster.utils.filtering.parse_filter_clause", return_value=q):
        filter_spec = {"include": {"username": "test"}, "exclude": {}}
        with pytest.raises(NotImplementedError):
            validate_lookups(User, filter_spec)


# Tests for validate_filters
@pytest.mark.django_db
def test_validate_filters():
    filter_spec = {"include": {"invalid_field": "test"}, "exclude": {}}
    with pytest.raises(ValidationError):
        validate_filters(User.objects.all(), filter_spec)
