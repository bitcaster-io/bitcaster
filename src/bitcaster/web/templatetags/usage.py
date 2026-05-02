from django import template
from django.db.models import Model
from django.urls import reverse

from bitcaster.utils.crontab import human_readable

register = template.Library()


@register.simple_tag()
def usage(target: Model) -> dict[str, str]:
    url_name = "admin:%s_%s_%s" % (target._meta.app_label, target._meta.model_name, "change")
    return {
        "type": target.__class__.__name__,
        "url": reverse(url_name, args=[target.pk]),
    }


@register.filter()
def cron_human_readable(s: str) -> str:
    return human_readable(s)
