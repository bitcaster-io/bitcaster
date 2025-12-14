from typing import TypedDict

from .json import JSONScalar

class FilterRule(TypedDict):
    field_path: str
    value: JSONScalar

FilterRuleSet = list[FilterRule]

class QuerysetFilter(TypedDict):
    include: list[FilterRule]
    exclude: list[FilterRule]
