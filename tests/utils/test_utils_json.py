import pytest
from django.utils import timezone

from bitcaster.dispatchers.base import Payload
from bitcaster.models import Event
from bitcaster.utils.json import (
    JsonUpdateMode,
    merge_dicts,
    override_dicts,
    process_dict,
    remove_dicts,
    safe_dumps,
    smart_dumps,
)


@pytest.mark.parametrize(
    "d1, d2, expected",
    [
        # Simple merge
        ({"a": 1}, {"b": 2}, {"a": 1, "b": 2}),
        # Override value
        ({"a": 1}, {"a": 2}, {"a": 2}),
        # Nested merge
        ({"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"b": 1, "c": 2}}),
        # Nested override
        ({"a": {"b": 1}}, {"a": {"b": 2}}, {"a": {"b": 2}}),
    ],
)
def test_merge_dicts(d1, d2, expected):
    assert merge_dicts(d1, d2) == expected


@pytest.mark.parametrize(
    "d1, d2, expected",
    [
        # Simple override
        ({"a": 1}, {"b": 2}, {"b": 2}),
        # Complete override
        ({"a": 1, "c": 3}, {"a": 2}, {"a": 2}),
        # Nested override
        ({"a": {"b": 1}}, {"a": {"c": 2}}, {"a": {"c": 2}}),
    ],
)
def test_override_dicts(d1, d2, expected):
    assert override_dicts(d1, d2) == expected


@pytest.mark.parametrize(
    "d1, d2, expected",
    [
        # Simple remove
        ({"a": 1, "b": 2}, {"b": 2}, {"a": 1}),
        # Remove non-existent key
        ({"a": 1}, {"b": 2}, {"a": 1}),
        # Nested remove
        ({"a": {"b": 1, "c": 2}}, {"a": {"c": 2}}, {"a": {"b": 1}}),
        # Remove all nested
        ({"a": {"b": 1}}, {"a": {"b": 1}}, {}),
    ],
)
def test_remove_dicts(d1, d2, expected):
    assert remove_dicts(d1, d2) == expected


@pytest.mark.parametrize(
    "mode, func",
    [
        (JsonUpdateMode.MERGE, merge_dicts),
        (JsonUpdateMode.OVERRIDE, override_dicts),
        (JsonUpdateMode.REMOVE, remove_dicts),
    ],
)
def test_process_dict(mode, func):
    d1 = {"a": 1, "b": {"c": 2}}
    d2 = {"b": {"d": 3}}
    assert process_dict(d1, d2, mode) == func(d1, d2)


def test_process_dict_rewrite():
    d1 = {"a": 1}
    d2 = {"b": 2}
    assert process_dict(d1, d2, JsonUpdateMode.REWRITE) == d2


def test_process_dict_invalid_mode():
    with pytest.raises(ValueError, match="Unknown JsonUpdateMode"):
        process_dict({}, {}, "invalid_mode")


@pytest.mark.parametrize(
    "o",
    [
        {
            "p": Payload(
                "",
                Event(),
                None,
            )
        },
        {"p": [1, 2, 3]},
        {"p": Event()},
        [1, 2, Event()],
        (1, 2, 3),
        timezone.now(),
    ],
)
def test_smart_dumps(o):
    assert smart_dumps(o)


def test_safe_dumps():
    assert safe_dumps({"a": 1}) == '{"a": 1}'
