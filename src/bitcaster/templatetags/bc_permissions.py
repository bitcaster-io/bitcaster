from django import template

from bitcaster.db.fields import Role

register = template.Library()


@register.simple_tag(takes_context=True, name='check_permissions')
def check_permissions(context, org=None, context_name='permissions'):
    """
        {% check_permissions %}
        {% check_permissions org %}
        {% check_permissions org as perms %}
    """
    organization = org or context.get('organization', None)
    if organization:
        user = context['request'].user
        membership = organization.membership_for(user=user)
        context[context_name] = {'owner': membership and membership.role == Role.OWNER,
                                 'admin': membership and membership.role == Role.ADMIN,
                                 'manager': membership and membership.role in [Role.OWNER, Role.ADMIN],
                                 }
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
