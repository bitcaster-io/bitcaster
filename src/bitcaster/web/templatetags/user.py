from datetime import datetime
from typing import TYPE_CHECKING

from django import template
from django.template import Context

if TYPE_CHECKING:
    from bitcaster.models import User

register = template.Library()


@register.simple_tag(takes_context=True)
def user_date(context: Context, d: datetime) -> str:
    user: "User" = context["user"]
    return user.format_date(d)
