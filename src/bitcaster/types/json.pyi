from __future__ import annotations

# Basic JSON scalar types
type JSONScalar = str | int | float | bool | None

# Recursive definition to allow nested lists and dictionaries
# Python 3.12+ handles this recursion natively without forward references
type JSONValue = JSONScalar | list[JSONValue] | dict[str, JSONValue]

# Helper alias for JSON arrays
type JSONArray = list[JSONValue]

# Helper alias for JSON objects (dictionaries)
type JSONDict = dict[str, JSONValue]

# The standard entry point for a JSON response or payload
type JSON = JSONDict
