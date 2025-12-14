JSONScalar = str | int | float | bool | None
JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
JSONArray = list[JSONValue]
JSON: type = dict[str, JSONValue]
