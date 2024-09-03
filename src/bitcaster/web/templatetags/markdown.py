import markdown
from django import template
from django.template.defaultfilters import stringfilter

from bitcaster.utils.markdown import BitcasterDocSiteExtension

register = template.Library()


@register.filter()
@stringfilter
def md(value: str) -> str:
    return markdown.markdown(
        value,
        extensions=[
            BitcasterDocSiteExtension(),
            # "markdown.extensions.fenced_code",
            # "markdown.extensions.meta",
            # "markdown.extensions.md_in_html",
            # "markdown.extensions.extra",
        ],
    )
