from unittest.mock import MagicMock

import pytest
from django.forms import inlineformset_factory
from django.template import Library
from rest_framework.fields import Field
from rest_framework.serializers import Serializer

from bitcaster.dispatchers import Email
from bitcaster.dispatchers.base import CoreDispatcher
from bitcaster.models import Application, DispatcherMetaData, Organization, User
from bitcaster.web.templatetags.bitcaster import (app_reverse,
                                                  channel_submit_row,
                                                  dispatcher_enabled, httpiefy,
                                                  jsonify, order_formset,
                                                  org_reverse, render_field,
                                                  render_serializer,
                                                  verbose_name,
                                                  verbose_name_plural,)

register = Library()


@pytest.mark.parametrize('value', ['', {'a': 1}])
def test_httpiefy(value):
    httpiefy(value)


@pytest.mark.parametrize('value', ['', {'a': 1}])
def test_jsonify(value):
    jsonify(value)


def test_verbose_name():
    assert verbose_name(User())


# @register.filter()
def test_verbose_name_plural():
    assert verbose_name_plural(User())


def test_channel_submit_row():
    assert channel_submit_row(MagicMock())


@pytest.mark.django_db
def test_app_reverse(application1):
    assert app_reverse({'application': application1}, 'app-edit')


@pytest.mark.django_db
def test_org_reverse(organization1):
    assert org_reverse({'organization': organization1}, 'org-applications')


@pytest.mark.django_db
def test_order_formset(application1):
    Formset = inlineformset_factory(Organization,
                                    Application,
                                    fields=('name',),
                                    extra=1)
    fs = Formset(instance=application1.organization)
    ordered = [f.instance for f in order_formset(fs)]
    assert not ordered[0].pk
    assert ordered[1].pk


def test_render_serializer():
    assert render_serializer(Serializer())


def test_render_field():
    class TestSerializer(Serializer):
        test_field = Field()

    serializer = TestSerializer()
    field = serializer['test_field']

    assert render_field(field, {})


@pytest.mark.django_db
def test_dispatcher_enable():
    DispatcherMetaData.objects.inspect()
    assert dispatcher_enabled(Email)


@pytest.mark.django_db
def test_dispatcher_not_enable():
    assert not dispatcher_enabled(CoreDispatcher)


#
# @register.simple_tag(takes_context=True)
# def oauth_button(context, channel: Channel):
#     label = channel.handler.render_button() or f'Authorise with {channel.handler.name}'
#     url = reverse('admin:bitcaster_channel_oauth_request', args=[channel.pk])
#     return mark_safe(f'<a href="{url}">{label}</a>')
#
#
# @register.simple_tag
# def render_serializer(serializer, template_pack=None):
#     style = {'template_pack': template_pack} if template_pack else {}
#     renderer = BitcasterHTMLFormRenderer()
#     return renderer.render(serializer.data, None, {'style': style})
#
#
# @register.simple_tag
# def render_field(field, style):
#     renderer = style.get('renderer', BitcasterHTMLFormRenderer())
#     return renderer.render_field(field, style)
#
#
# @register.simple_tag(name='org-url', takes_context=True)
# def org_reverse(context, url_name, *args, **kwargs):
#     org = context['organization']
#     return reverse(url_name, args=(org.slug,) + args, **kwargs)
#
#
# @register.simple_tag(name='app-url', takes_context=True)
# def app_reverse(context, url_name, *args, **kwargs):
#     org = context['organization']
#     app = context['application']
#     return reverse(url_name, args=(org.slug,
#                                    app.slug) + args, **kwargs)
#
#
# @register.inclusion_tag('admin/bitcaster/configurable_submit_line.html', takes_context=True)
# def channel_submit_row(context):
#     """
#     Display the row of buttons for delete and save.
#     """
#     change = context['change']
#     is_popup = context['is_popup']
#     save_as = context['save_as']
#     show_save = context.get('show_save', True)
#     show_save_and_continue = context.get('show_save_and_continue', True)
#
#     can_delete = context['has_delete_permission']
#     can_add = context['has_add_permission']
#     can_change = context['has_change_permission']
#
#     ctx = Context(context)
#     ctx.update({
#         'show_delete_link': (not is_popup and
#                              can_delete and
#                              change and
#                              context.get('show_delete', True)
#                              ),
#         'show_save_as_new': not is_popup and change and save_as,
#         'show_save_and_add_another': (can_add and
#                                       not is_popup and
#                                       (not save_as or context['add'])
#                                       ),
#         'show_save_and_continue': (not is_popup and can_change and show_save_and_continue),
#         'show_save': show_save,
#     })
#     return ctx
#
#
# @register.filter()
# def display_queryset(qs, fields):
#     fields = fields.split(',')
#     return mark_safe(', '.join(qs.values_list(*fields, flat=True)))
#
#
# @register.filter()
# def describe_channels(channels):
#     return mark_safe(', '.join([f'<span class=enabled{c.enabled}>{c.name}</span>' for c in channels.all()]))
