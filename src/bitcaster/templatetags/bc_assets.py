from functools import lru_cache
from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static as _static
from django.urls import reverse
from django.utils.safestring import mark_safe
from strategy_field.utils import fqn

import bitcaster
from bitcaster.utils.http import absolute_uri

register = template.Library()


# def get_asset_url(path):
#     # return _static(path)
#     return '{}/{}'.format(settings.STATIC_URL.rstrip('/'), path,)


@register.simple_tag
def asset(path):
    """
    Join the given path with the STATIC_URL setting.

    Usage::

        {% static path [as varname] %}

    Examples::

        {% static "myapp/css/base.css" %}
        {% static variable_with_path %}
        {% static "myapp/css/base.css" as admin_base_css %}
        {% static variable_with_path as varname %}
    """
    commit = bitcaster.get_full_version()
    return mark_safe('{0}?{1}'.format(_static(path), commit))


@register.simple_tag
def aasset(path):
    """
    Join the given path with the STATIC_URL setting.

    Usage::

        {% static path [as varname] %}

    Examples::

        {% static "myapp/css/base.css" %}
        {% static variable_with_path %}
        {% static "myapp/css/base.css" as admin_base_css %}
        {% static variable_with_path as varname %}
    """
    commit = bitcaster.get_full_version()
    return '%s?%s' % (absolute_uri(_static(path)), commit)


@register.simple_tag
def aurl(name, *args, **kwargs):
    return absolute_uri(reverse(name, *args, **kwargs))


@lru_cache(100)
@register.simple_tag
def channel_icon_url(channel):
    if channel.handler:
        name = fqn(channel.handler).split('.')[-1]
    a = Path(settings.STATIC_ROOT) / f'bitcaster/images/icons/{name.lower()}.png'
    if a.exists():
        return settings.STATIC_URL + f'bitcaster/images/icons/{name.lower()}.png'
    return '/static/bitcaster/images/plugin.png'


@lru_cache(100)
@register.simple_tag
def plugin_icon_url(handler):
    if handler:
        name = fqn(handler).split('.')[-1]
        a = Path(settings.STATIC_ROOT) / f'bitcaster/images/icons/{name.lower()}.png'
        if a.exists():
            return settings.STATIC_URL + f'bitcaster/images/icons/{name.lower()}.png'
    return '/static/bitcaster/images/plugin.png'


@lru_cache(100)
@register.simple_tag
def handler_icon_url(handler):
    name = fqn(handler).split('.')[-1]
    a = Path(settings.STATIC_ROOT) / f'bitcaster/images/icons/{name.lower()}.png'
    if a.exists():
        return settings.STATIC_URL + f'bitcaster/images/icons/{name.lower()}.png'
    return '/static/bitcaster/images/plugin.png'
