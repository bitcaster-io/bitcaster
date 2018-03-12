from __future__ import absolute_import

from constance import config
from django.conf import settings
from django.http import HttpResponseRedirect


class SetupMiddleware(object):
    """
    Ensure that we have proper security headers set
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not bool(config.INITIALIZED):
            if request.path != '/setup/' and not request.path.startswith(settings.STATIC_URL):
                return HttpResponseRedirect("/setup/")
        return self.get_response(request)
