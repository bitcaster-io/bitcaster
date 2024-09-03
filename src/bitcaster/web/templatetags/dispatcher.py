from typing import Any

from django import template
from django.utils.safestring import mark_safe

from bitcaster.web.templatetags.markdown import md

register = template.Library()


@register.filter
def help_doc(d: "Any") -> str:
    text = f"""{d.help_text}"""
    return mark_safe(md(text))  # nosec
