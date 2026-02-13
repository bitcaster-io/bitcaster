from typing import Any

from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.urls import reverse
from django.utils.safestring import mark_safe

from bitcaster.utils.crontab import human_readable

register = template.Library()


@register.simple_tag()
def usage(target: Any) -> dict[str, str]:
    return {
        "type": target.__class__.__name__,
        "url": reverse(admin_urlname(target._meta, mark_safe("change")), args=[target.pk]),  # nosec  # noqa: S308
    }


@register.filter()
def cron_human_readable(s: str) -> str:
    return human_readable(s)
