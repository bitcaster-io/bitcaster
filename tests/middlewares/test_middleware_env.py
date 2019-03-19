from __future__ import absolute_import

from django.http import HttpResponse

from bitcaster.middleware.env import BitcasterEnvMiddleware, clear_request
from bitcaster.state import state


def test_bitcasterenvmiddleware_call(rf):
    request = rf.get('/')
    m = BitcasterEnvMiddleware(lambda r: HttpResponse('Ok'))
    m(request)
    assert state.request == request


def test_clear_request(**kwargs):
    clear_request()
    assert not state.data
