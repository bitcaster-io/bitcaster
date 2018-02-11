# -*- coding: utf-8 -*-
import json
from django.template import Library

register = Library()


@register.filter()
def httpiefy(value):
    if not value:
        return ""
    return " ".join(["%s=%s" % (k, v) for k, v in value.items()])


@register.filter()
def jsonify(value):
    return json.dumps(value)
