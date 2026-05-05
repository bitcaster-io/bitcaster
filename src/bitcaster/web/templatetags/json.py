from typing import Any

import json

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def beautify(json_object: Any) -> str:
    json_str = json.dumps(json_object, indent=4, sort_keys=True)
    formatter = HtmlFormatter(cssclass="json", linenos="table", wrapcode=True)
    value = highlight(json_str, JsonLexer(), formatter)

    return mark_safe(value)  # nosec  # noqa: S308


@register.filter
def get_item(d: dict[str, Any], key: Any) -> Any:
    return d.get(key)
