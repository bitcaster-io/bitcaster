# -*- coding: utf-8 -*-
import json
from django.template import Context, Library

register = Library()


@register.filter()
def httpiefy(value):
    if not value:
        return ""
    return " ".join(["%s=%s" % (k, v) for k, v in value.items()])


@register.filter()
def jsonify(value):
    return json.dumps(value)


@register.inclusion_tag('admin/mercury/channel/submit_line.html', takes_context=True)
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
