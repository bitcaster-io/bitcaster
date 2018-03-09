from django import template

from bitcaster.security import is_owner

register = template.Library()


@register.simple_tag(takes_context=True, name='check_permissions')
def check_permissions(context, org=None, context_name="permissions"):
    """
        {% check_permissions %}
        {% check_permissions org %}
        {% check_permissions org as perms %}
    """
    organization = org or context["organization"]
    user = context["request"].user
    context[context_name] = {'owner': is_owner(user, organization)}
    return ""
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
