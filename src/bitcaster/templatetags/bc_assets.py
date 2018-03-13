from django import template
from django.conf import settings
from django.urls import reverse

import bitcaster
from bitcaster.utils.http import absolute_uri

register = template.Library()


def get_asset_url(path):
    return '{}/{}'.format(
        settings.STATIC_URL.rstrip('/'),
        path,
    )


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
    return get_asset_url(f"{path}?{commit}")

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
    return absolute_uri(get_asset_url(f"{path}?{commit}"))

@register.simple_tag
def aurl(name, *args, **kwargs):
    return absolute_uri(reverse(name, *args, **kwargs))
