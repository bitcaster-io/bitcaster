from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models import Model
from django.urls import reverse

from bitcaster.utils.crontab import human_readable

register = template.Library()


@register.simple_tag()
def usage(target: Model) -> dict[str, str]:
    return {
        "type": target.__class__.__name__,
        "url": reverse(admin_urlname(target._meta, "change"), args=[target.pk]),  # type: ignore[arg-type]
    }


@register.filter()
def cron_human_readable(s: str) -> str:
    return human_readable(s)
