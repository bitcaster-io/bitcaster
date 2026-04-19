from typing import TYPE_CHECKING, Any, TypeVar, cast

from django.core.exceptions import FieldError, ValidationError
from django.db import models
from django.db.models import Q
from django_regex.utils import RegexList
from jsonschema import ValidationError as SchemaValidationError
from jsonschema import validate

if TYPE_CHECKING:
    from bitcaster.types.django import QuerySetOrManager
    from bitcaster.types.filtering import AllowedFilters, QuerysetFilter
    from bitcaster.types.json import JSON

    M = TypeVar("M", bound=models.Model)

schema = {
    "title": "QuerysetFilter",
    "type": "object",
    "required": ["include", "exclude"],
    "additionalProperties": False,
    "properties": {"include": {"$ref": "#/$defs/filterGroup"}, "exclude": {"$ref": "#/$defs/filterGroup"}},
    "$defs": {
        "jsonScalar": {"oneOf": [{"type": "string"}, {"type": "number"}, {"type": "boolean"}, {"type": "null"}]},
        "jsonArray": {"type": "array", "items": {"$ref": "#/$defs/jsonScalar"}},
        "explicitRule": {
            "type": "object",
            "additionalProperties": False,
            "required": ["field_path", "value"],
            "properties": {
                "field_path": {"type": "string", "minLength": 1},
                "value": {"oneOf": [{"$ref": "#/$defs/jsonScalar"}, {"$ref": "#/$defs/jsonArray"}]},
            },
        },
        "shorthandRule": {
            "type": "object",
            "minProperties": 1,
            "additionalProperties": {"oneOf": [{"$ref": "#/$defs/jsonScalar"}, {"$ref": "#/$defs/jsonArray"}]},
        },
        "filterRule": {"oneOf": [{"$ref": "#/$defs/explicitRule"}, {"$ref": "#/$defs/shorthandRule"}]},
        "singleRuleGroup": {"$ref": "#/$defs/filterRule"},
        "orGroup": {"type": "array", "items": {"$ref": "#/$defs/filterRule"}, "minItems": 1},
        "andGroup": {"type": "array", "items": {"$ref": "#/$defs/orGroup"}, "minItems": 1},
        "emptyListGroup": {"type": "array", "maxItems": 0},
        "emptyDictGroup": {"type": "object", "maxProperties": 0},
        "filterGroup": {
            "oneOf": [
                {"$ref": "#/$defs/emptyListGroup"},
                {"$ref": "#/$defs/emptyDictGroup"},
                {"$ref": "#/$defs/singleRuleGroup"},
                {"$ref": "#/$defs/orGroup"},
                {"$ref": "#/$defs/andGroup"},
            ]
        },
    },
}
DEFAULT_INVALID_LOOKUPS = [".*password.*", ".*token.*", ".*secret.*", ".*key.*"]

DEFAULT_MODEL_INVALID_LOOKUPS = {"bitcaster.User": [r".*_password.*"]}


def clean_field_error_message(message: str) -> str:
    return message


def validate_lookups(model: "type[models.Model]", filter_spec: "QuerysetFilter") -> None:
    def _dummy_render(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _dummy_render(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_dummy_render(v) for v in obj]
        if isinstance(obj, str) and "{{" in obj:
            return "dummy"
        return obj

    clean_spec = _dummy_render(filter_spec)
    for family in ["include", "exclude"]:
        if parsed := parse_filter_clause(clean_spec.get(family, [])):
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            rules = RegexList(DEFAULT_MODEL_INVALID_LOOKUPS.get(model_name, []) + DEFAULT_INVALID_LOOKUPS)
            for i, entry in enumerate(parsed.children, 1):
                if not isinstance(entry, tuple):
                    raise NotImplementedError(f"Not implemented lookup: '{entry}' '{entry.__class__}'")
                if entry[0] in rules:
                    raise ValidationError(f"Unauthorised lookup: '{entry[0]}' in {family}[{i}]")


def validate_schema(d: "dict[str, Any] | QuerysetFilter") -> None:
    try:
        validate(instance=d, schema=schema)
    except SchemaValidationError as e:
        raise ValidationError(e.message) from None


def validate_filters(queryset: "QuerySetOrManager[M]", d: "AllowedFilters") -> None:
    def _dummy_render(obj: Any) -> "AllowedFilters":
        if isinstance(obj, dict):
            return {k: _dummy_render(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_dummy_render(v) for v in obj]
        if isinstance(obj, str) and "{{" in obj:
            return "dummy"
        return obj

    try:
        clean_data = _dummy_render(d)
        fm = FilterManager(queryset=queryset, filter_spec=clean_data)
        fm.filter().first()
    except (FieldError, ValidationError) as e:
        raise ValidationError(clean_field_error_message(str(e))) from None


def normalize_groups(data: "JSON | list[JSON] | list[list[JSON]]") -> "list[list[JSON]]":
    """Normalize input into list[list[dict]].

    Accepted:
    - dict
    - list[dict]
    - list[list[dict]]
    """
    if isinstance(data, dict):
        return [[data]]

    if isinstance(data, list):
        if not data:
            return []
        if all(isinstance(item, dict) for item in data):
            return [cast("list[JSON]", data)]

        if all(isinstance(item, list) and all(isinstance(d, dict) for d in item) for item in data):
            return cast("list[list[JSON]]", data)

    raise TypeError(f"Invalid filter structure: {data!r}")


def dict_to_q(data: "JSON") -> "models.Q":
    return models.Q(**data)


def or_group_to_q(group: "list[JSON]") -> "models.Q":
    q = models.Q()
    for item in group:
        q |= dict_to_q(item)
    return q


def parse_filter_clause(data: "JSON | list[JSON] | list[list[JSON]]") -> "models.Q":
    groups = normalize_groups(data)

    q = models.Q()
    for group in groups:
        q &= or_group_to_q(group)

    return q


class FilterManager[M]:
    def __init__(self, queryset: "QuerySetOrManager[M]", filter_spec: "AllowedFilters"):
        self.filter_spec = filter_spec

        self.queryset = queryset

    @classmethod
    def parse(cls, filter_spec: "AllowedFilters") -> tuple[Q, Q]:
        spec = cast("dict[str, Any]", filter_spec) if isinstance(filter_spec, dict) else {}
        includes = parse_filter_clause(spec.get("include", []))
        excludes = parse_filter_clause(spec.get("exclude", []))
        return includes, excludes

    def filter(self, *args: Any, **kwargs: Any) -> "models.QuerySet[M]":
        if self.filter_spec:
            includes, excludes = self.parse(self.filter_spec)
            return self.queryset.filter(includes).exclude(excludes).filter(*args, **kwargs)
        return self.queryset.filter(*args, **kwargs)
