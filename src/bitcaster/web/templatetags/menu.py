from django import template

from bitcaster.utils.reflect import classname, fqn

register = template.Library()


@register.filter()
def menu_item(view, string):
    if string in fqn(view).lower():
        return 'active'


@register.filter(name='fqn')
def _fqn(obj):
    return fqn(obj)


@register.filter(name='classname')
def _classname(obj):
    return classname(obj)
