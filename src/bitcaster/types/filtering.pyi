from typing import Any, TypedDict

from .json import JSON

FilterRule = JSON

FilterRuleSet = list[FilterRule]

class QuerysetFilter(TypedDict):
    include: list[FilterRule]
    exclude: list[FilterRule]

AllowedFilters = dict[str, Any] | QuerysetFilter
