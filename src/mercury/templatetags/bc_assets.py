from django import template
from django.conf import settings

import mercury
from mercury.utils.http import absolute_uri

register = template.Library()


def get_asset_url(path):
    """
    Returns a versioned asset URL (located within Sentry's static files).

    Example:
      {% asset_url 'sentry' 'dist/sentry.css' %}
      =>  "/_static/74d127b78dc7daf2c51f/sentry/dist/sentry.css"
    """
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
    commit = mercury.get_full_version()
    return absolute_uri(get_asset_url(f"{path}?{commit}"))
