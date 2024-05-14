from django import template
from django.utils.safestring import mark_safe

from bitcaster.dispatchers.base import Dispatcher
from bitcaster.web.templatetags.markdown import md

register = template.Library()


@register.filter
def help_doc(d: "Dispatcher") -> str:
    return mark_safe(md(d.help_text))  # nosec
