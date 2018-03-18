from django import template

register = template.Library()


@register.simple_tag
def channel_type(channel):
    if channel.system:
        return "[system]"
    elif not channel.application:
        return "[org]"
    elif channel.application:
        return "[app]"
