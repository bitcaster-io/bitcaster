from __future__ import absolute_import

from constance import config
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse


class SetupMiddleware(object):
    """
    Ensure that we have proper security headers set
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        destination = reverse('setup')
        if not bool(config.INITIALIZED):
            if request.path != destination and not request.path.endswith(settings.STATIC_URL):
                return HttpResponseRedirect(destination)
        return self.get_response(request)
