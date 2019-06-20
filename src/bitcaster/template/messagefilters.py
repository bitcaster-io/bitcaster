import pytz
from django.template import Library

register = Library()


@register.simple_tag(name='user_timezone', takes_context=True)
def user_timezone(context, date):
    user = context['subscriber']
    return date.replace(tzinfo=pytz.timezone(str(user.timezone)))
