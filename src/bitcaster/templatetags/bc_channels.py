from django import template
from django.conf import settings
from django.urls import reverse

import bitcaster
from bitcaster.utils.http import absolute_uri

register = template.Library()


@register.simple_tag
def channel_type(channel):
    if channel.system:
        return "[system]"
    elif not channel.application:
        return "[org]"
    elif channel.application:
        return "[app]"
