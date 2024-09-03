from typing import Any

from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag()
def usage(target: Any) -> dict[str, str]:
    return {
        "type": target.__class__.__name__,
        "url": reverse(admin_urlname(target._meta, mark_safe("change")), args=[target.pk]),  # nosec
    }
