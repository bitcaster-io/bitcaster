import json
from typing import Any

from django import template
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

register = template.Library()


@register.filter()
def beautify(json_object: Any) -> str:
    json_str = json.dumps(json_object, indent=4, sort_keys=True)
    formatter = HtmlFormatter(cssclass="json", linenos="table", wrapcode=True)
    value = highlight(json_str, JsonLexer(), formatter)

    return mark_safe(value)  # nosec  # noqa: S308
