from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def metric(label, value):
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
    return mark_safe(f'''<div class="block p-1">
                <div class="d-inline-block">{label}</div>
                <div class="d-inline-block pull-right">{value}</div>
            </div>''')
