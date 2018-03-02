from __future__ import absolute_import

import redis.exceptions
from constance import config
from django.db import connection, OperationalError
from django.http import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse


class SetupMiddleware(object):
    """
    Ensure that we have proper security headers set
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not config.INITIALIZED:
            if request.path != '/setup/':
                return HttpResponseRedirect("/setup/")
        return response
