import json
from typing import TYPE_CHECKING, Any

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model, TextChoices

from bitcaster.dispatchers.base import Payload

if TYPE_CHECKING:
    from bitcaster.types.json import JSON


class BitcasterEncoder(DjangoJSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Payload):
            return o.as_dict()
        if isinstance(o, (list | tuple)):
            return [smart_dumps(e) for e in o]
        if isinstance(o, Model):
            return str(o)
        return super().default(o)


def smart_dumps(obj: Any) -> Any:
    return json.dumps(obj, cls=BitcasterEncoder)


class JsonUpdateMode(TextChoices):
    MERGE = "merge"
    REMOVE = "remove"
    OVERRIDE = "override"
    REWRITE = "rewrite"
    IGNORE = "ignore"


def process_dict(d1: "JSON", d2: "JSON", mode: JsonUpdateMode) -> "JSON":
    if mode == JsonUpdateMode.MERGE:
        return merge_dicts(d1, d2)
    if mode == JsonUpdateMode.OVERRIDE:
        return override_dicts(d1, d2)
    if mode == JsonUpdateMode.REMOVE:
        return remove_dicts(d1, d2)
    if mode == JsonUpdateMode.REWRITE:
        return d2
    raise ValueError(f"Unknown JsonUpdateMode: {mode}")


def merge_dicts(d1: "JSON", d2: "JSON") -> "JSON":
    """Deep merge.

    - dicts merge recursively
    - other values from d2 override d1
    """
    result = d1.copy()

    for key, value in d2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


def override_dicts(d1: "JSON", d2: "JSON") -> "JSON":
    """Shallow override.

    - values in d2 completely replace values in d1
    """
    result = d1.copy()
    result.update(d2)
    return d2


def remove_dicts(d1: "JSON", d2: "JSON") -> "JSON":
    """Remove keys in d1 if they appear in d2.

    If both values are dicts → remove recursively.
    """
    result = d1.copy()
    for key, value in d2.items():
        if key not in result:
            continue

        if isinstance(result[key], dict) and isinstance(value, dict):
            nested = remove_dicts(result[key], value)
            if nested:
                result[key] = nested
            else:
                del result[key]
        else:
            del result[key]

    return result
