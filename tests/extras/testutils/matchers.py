from typing import TYPE_CHECKING

import re

import pytest

from django_regex.utils import RegexList as _RegexList

if TYPE_CHECKING:
    from typing import Any, Iterable


class RegexList(_RegexList):  # type: ignore[misc]
    def extend(self, __iterable: "Iterable[Any]") -> None:
        for e in __iterable:
            self.append(e)


def list_match(bucket: "Iterable[str]", target: str):
    rex = re.compile(target)
    for entry in bucket:
        m = rex.match(entry)
        if m and m.group():
            return True
    return False


def assert_list_match(bucket: "Iterable[str]", target: str):
    if not list_match(bucket, target):
        pytest.fail(f"No match for '{target}'")
