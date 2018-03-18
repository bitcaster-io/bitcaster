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


@register.simple_tag(takes_context=True)
def channel_configurable(context, channel):
    if 'application' in context:
        return channel.application == context['application']
    if 'organization' in context:
        return channel.organization == context['organization']
    return channel.system
