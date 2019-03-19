from unittest.mock import Mock

from django.http import HttpResponse

from bitcaster.middleware.message import MessageMiddleware


def test_messagemiddleware_happy_path(rf):
    request = rf.get('/')
    request.session = Mock()
    m = MessageMiddleware(lambda r: HttpResponse('Ok'))

    m.process_request(request)

    m.process_response(request, HttpResponse('Ok'))
    assert request._messages.request
    assert request._alarms.request


def test_messagemiddleware_partial(rf):
    request = rf.get('/')
    request.session = Mock()
    request.session = Mock()
    m = MessageMiddleware(lambda r: HttpResponse('Ok'))
    response = m.process_response(request, HttpResponse('Ok'))
    assert response
