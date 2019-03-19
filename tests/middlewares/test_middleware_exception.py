from unittest.mock import Mock

from django.http import HttpResponse

from bitcaster.exceptions import NotMemberOfOrganization
from bitcaster.middleware.exception import ExceptionHandlerMiddleware


def test_exceptionhandlermiddleware_call(rf):
    request = rf.get('/aaa/', HTTP_REFERER='/from/')
    request._alarms = Mock()
    m = ExceptionHandlerMiddleware(lambda r: HttpResponse('Ok'))
    m(request)
    response = m.process_exception(request, NotMemberOfOrganization(Mock()))
    assert response.status_code == 302
    assert response['Location'] == '/from/'


def test_exceptionhandlermiddleware_noop(rf):
    request = rf.get('/aaa/', HTTP_REFERER='/from/')
    request._alarms = Mock()
    m = ExceptionHandlerMiddleware(lambda r: HttpResponse('Ok'))
    m(request)
    response = m.process_exception(request, ValueError())
    assert response is None
