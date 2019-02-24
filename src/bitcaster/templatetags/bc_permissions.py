from django import template

from bitcaster.backends import PERMISSIONS
from bitcaster.models import Application, Organization

register = template.Library()


class AuthWrapper:
    __name__ = 'AuthWrapper'

    def __init__(self, perms):
        self.perms = [perm.split(':')[1] for perm in perms]

    def __repr__(self):
        return repr(self.perms)

    def __getitem__(self, name):
        return bool(name in self.perms)

    def __contains__(self, perm_name):
        return perm_name in self.perms


@register.simple_tag(takes_context=True, name='check_permissions')
def check_permissions(context, target, context_name='permissions'):
    """
        {% check_permissions org %}
        {% check_permissions org as perms %}
    """
    user = context['request'].user
    if isinstance(target, Organization):
        perms = [perm for perm in PERMISSIONS if perm.startswith('org') and user.has_perm(perm, target)]
    elif isinstance(target, Application):
        perms = [perm for perm in PERMISSIONS if perm.startswith('app') and user.has_perm(perm, target)]
    else:
        perms = []
    # user = context['request'].user
    #  membership = organization.membership_for(user=user)
    #  owner = (organization.owner == user) or (membership and membership.role == Role.OWNER)
    #  context[context_name] = {'owner': owner,
    #                           'admin': membership and membership.role == Role.ADMIN,
    #                           'manager': owner or (membership and membership.role in [Role.OWNER,
    #                                                                                   Role.ADMIN]),
    #                           }
    context[context_name] = AuthWrapper(perms)
    return ''

#
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
