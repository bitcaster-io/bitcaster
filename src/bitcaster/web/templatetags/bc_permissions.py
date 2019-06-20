from django import template
from django.template.defaultfilters import slugify
from django.utils.safestring import mark_safe

from bitcaster.models import Application, Organization
from bitcaster.security import ALL_PERMISSIONS
from bitcaster.utils.reflect import classname

register = template.Library()


class AuthWrapper:
    __name__ = 'AuthWrapper'

    def __init__(self, perms):
        self.perms = perms

    def __repr__(self):
        return repr(self.perms)

    def __getitem__(self, name):
        return bool(name in self.perms)


class CheckPermissions(template.Node):
    def __init__(self, target, var_name):
        self.target = target
        self.var_name = var_name or 'permissions'

    def render(self, context):
        user = context['request'].user
        target = context[self.target]
        if isinstance(target, Organization):
            perms = [perm for perm in ALL_PERMISSIONS if user.has_perm(perm, target)]
        elif isinstance(target, Application):
            perms = [perm for perm in ALL_PERMISSIONS if user.has_perm(perm, target)]
        else:
            perms = []
        context[self.var_name] = AuthWrapper(perms)
        return ''


@register.tag(name='check_permissions')
def check_permissions(parser, token):
    try:
        tag, *args = token.contents.split(None)
        target = args[0]
    except IndexError:
        raise template.TemplateSyntaxError('%r tag requires arguments'
                                           % token.contents.split()[0])
    var_name = None
    if len(args) > 1:
        if args[1] != 'as':
            raise template.TemplateSyntaxError('%r tag had invalid arguments' % str(args))
        var_name = args[2]

    return CheckPermissions(target, var_name)


@register.simple_tag(takes_context=True)
def button(context, href, has_perm, icon, label, toggler=None, viewname='', extra_css_if_test='border border-dark'):
    view = context['view']
    if toggler is not None:
        if toggler:
            label = label.split(':')[0]
            icon = icon.split(':')[0]
        else:
            label = label.split(':')[1]
            icon = icon.split(':')[1]

    params = {'disabled': 'disabled',
              'icon': icon,
              'css': '',
              'title': label,
              'id': slugify(href),
              'href': ''}

    if classname(view) == viewname:
        params['css'] = extra_css_if_test

    if has_perm:
        params.update({'disabled': '',
                       'title': label,
                       'href': href
                       })
    return mark_safe('''<a class="btn btn-light %(disabled)s %(css)s "
                           data-toggle="tooltip" title="%(title)s"
                           id="%(id)s"
                           href="%(href)s">
                            <i class="%(icon)s pointer"></i>
                        </a>''' % params)
# @register.filter
# def is_admin(user, organization):
#     return user.has_perm('')
#
#
# @register.filter
# def can_configure(user, target):
#     return user.has_perm('configure', target)
#
# #
# @register.assignment_tag(takes_context=True)
# def get_user_perm(context, perm):
#     try:
#         request = context['request']
#         obj = Profile.objects.get(user=request.user)
#         obj_perms = obj.permission_tags.all()
#         flag = False
#         for p in obj_perms:
#             if perm.lower() == p.codename.lower():
#                 flag = True
#                 return flag
#         return flag
#     except Exception as e:
#         return ""
