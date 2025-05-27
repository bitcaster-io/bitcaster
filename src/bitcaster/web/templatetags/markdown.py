from typing import Any

import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from bitcaster.utils.markdown import BitcasterDocSiteExtension

register = template.Library()


@register.filter()
@stringfilter
def md(value: str) -> str:
    return markdown.markdown(
        value,
        extensions=[
            BitcasterDocSiteExtension(),
            "markdown.extensions.fenced_code",
            "markdown.extensions.def_list",
            "markdown.extensions.attr_list",
            "markdown.extensions.nl2br",
            "markdown.extensions.md_in_html",
            "markdown.extensions.extra",
            "markdown.extensions.smarty",
            "markdown.extensions.tables",
        ],
    )


@register.filter
def help_doc(d: "Any") -> str:
    text = getattr(d, "help_text", "")
    return mark_safe(md(text))  # nosec  # noqa: S308
