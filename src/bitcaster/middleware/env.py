from __future__ import absolute_import

from django.core.signals import request_finished

from bitcaster.state import state


class BitcasterEnvMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        state.request = request
        response = self.get_response(request)
        return response


def clear_request(**kwargs):
    state.clear()


request_finished.connect(clear_request)
