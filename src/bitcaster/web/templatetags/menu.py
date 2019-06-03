from django import template

from bitcaster.utils.reflect import fqn

register = template.Library()


@register.filter()
def menu_item(view, string):
    if string in fqn(view).lower():
        return 'active'
