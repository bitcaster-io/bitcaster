import markdown
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter()
@stringfilter
def md(value: str) -> str:
    return markdown.markdown(
        value,
        extensions=[
            # "markdown.extensions.fenced_code",
            "markdown.extensions.md_in_html",
            "markdown.extensions.wikilinks",
            "markdown.extensions.extra",
        ],
    )
