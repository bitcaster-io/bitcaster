from __future__ import absolute_import

from constance import config
from django.http import HttpResponseRedirect


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
