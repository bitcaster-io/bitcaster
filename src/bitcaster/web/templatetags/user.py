from datetime import datetime
from typing import TYPE_CHECKING

from django import template
from django.template import Context
from django.utils import timezone

if TYPE_CHECKING:
    from bitcaster.models import User

register = template.Library()


@register.simple_tag(takes_context=True)
def user_date(context: Context, d: datetime) -> str:
    user: "User" = context["request"].user
    if not d:
        return ""
    if user.is_authenticated:
        d = timezone.localtime(d, user.timezone)
    return user.format_date(d)


@register.simple_tag(takes_context=True)
def user_datetime(context: Context, d: datetime) -> str:
    user: "User" = context["request"].user
    if not d:
        return ""
    if user.is_authenticated:
        d = timezone.localtime(d, user.timezone)
    return user.format_datetime(d)
