from __future__ import absolute_import

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
        # if request.path != '/setup/':
        #     return HttpResponseRedirect("/setup/")
        return response
        # ctx = {}
        # return TemplateResponse(request, "bitcaster/setup.html", ctx)
