# -*- coding: utf-8 -*-
import json

from django.template import Context, Library
from django.urls import reverse
from django.utils.safestring import mark_safe

from bitcaster.api.renderers import BitcasterHTMLFormRenderer
from bitcaster.models import Channel

register = Library()


@register.filter()
def httpiefy(value):
    if not value:
        return ""
    return " ".join(["%s=%s" % (k, v) for k, v in value.items()])


@register.filter()
def jsonify(value):
    return json.dumps(value)


@register.simple_tag(takes_context=True)
def oauth_button(context, channel: Channel):
    label = channel.handler.render_button() or f'Authorise with {channel.handler.name}'
    url = reverse("admin:bitcaster_channel_oauth_request", args=[channel.pk])
    return mark_safe(f'<a href="{url}">{label}</a>')


@register.simple_tag
def render_serializer(serializer, template_pack=None):
    style = {'template_pack': template_pack} if template_pack else {}
    renderer = BitcasterHTMLFormRenderer()
    return renderer.render(serializer.data, None, {'style': style})


@register.simple_tag
def render_field(field, style):
    renderer = style.get('renderer', BitcasterHTMLFormRenderer())
    return renderer.render_field(field, style)


@register.simple_tag(name="org-url", takes_context=True)
def org_reverse(context, url_name, *args, **kwargs):
    org = context["organization"]
    return reverse(url_name, args=(org.slug,) + args, **kwargs)


@register.simple_tag(name="app-url", takes_context=True)
def app_reverse(context, url_name, *args, **kwargs):
    org = context["organization"]
    app = context["application"]
    return reverse(url_name, args=(org.slug,
                                   app.slug) + args, **kwargs)


@register.inclusion_tag('admin/bitcaster/configurable_submit_line.html', takes_context=True)
def channel_submit_row(context):
    """
    Display the row of buttons for delete and save.
    """
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    show_save = context.get('show_save', True)
    show_save_and_continue = context.get('show_save_and_continue', True)

    can_delete = context['has_delete_permission']
    can_add = context['has_add_permission']
    can_change = context['has_change_permission']

    ctx = Context(context)
    ctx.update({
        'show_delete_link': (not is_popup and
                             can_delete and
                             change and
                             context.get('show_delete', True)
                             ),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': (can_add and
                                      not is_popup and
                                      (not save_as or context['add'])
                                      ),
        'show_save_and_continue': (not is_popup and
                                   can_change and
                                   show_save_and_continue),
        'show_save': show_save,
    })
    return ctx


@register.filter()
def describe_channels(channels):
    return mark_safe(", ".join([f"<span class=enabled{c.enabled}>{c.name}</span>" for c in channels.all()]))
