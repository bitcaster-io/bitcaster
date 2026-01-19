import base64
import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj, cls=DjangoJSONEncoder))


@register.filter(is_safe=True)
def atob(x):
    return base64.b64decode(x)


@register.filter(is_safe=True)
def btoa(x):
    return base64.b64encode(bytes(x, "utf-8")).decode("utf-8")


#
# @register.filter(name="json", is_safe=True)
# def as_json(x):
#     return json.dumps(x)
#
#
# @register.inclusion_tag("pwa/_pwa.html", takes_context=True)
# def progressive_web_app_meta(context):
#     request = context["request"]
#     return {
#         "ua": request.user_agent,
#         **{
#             setting_name: getattr(app_settings, setting_name)
#             for setting_name in dir(app_settings)
#             if setting_name.startswith("PWA_")
#         },
#     }
