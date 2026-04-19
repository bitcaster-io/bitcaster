from typing import TypedDict

from .json import JSON, JSONScalar, JSONValue

# A rule can be a single filter dict, a list of dicts,
# or nested lists for complex OR/AND logic
type FilterRule = dict[str, JSONValue] | list[JSON] | list[list[JSON]] | list[JSONScalar]

# A set of rules is simply a list of the above
type FilterRuleSet = list[FilterRule]

# Define the structure for include/exclude logic
class QuerysetFilter(TypedDict):
    include: FilterRuleSet
    exclude: FilterRuleSet

# Recursive definition for allowed filters
# Replaced dict[str, Any] with JSON to maintain type safety
type AllowedFilters = (
    JSON
    | QuerysetFilter
    | list["AllowedFilters"]  # Recursive reference using quotes or lazy type
    | str
)
