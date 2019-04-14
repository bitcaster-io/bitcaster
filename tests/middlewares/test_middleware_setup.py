from constance.test import override_config
from django.http import HttpResponse

from bitcaster.middleware.setup import SetupMiddleware


def test_setupmiddleware_call_not_configured(rf):
    request = rf.get('/')
    m = SetupMiddleware(lambda r: HttpResponse('Ok'))
    response = m(request)

    assert response.status_code == 302
    assert response['Location'] == '/setup/'


def test_setupmiddleware_call_no_recurse(rf):
    request = rf.get('/setup/')
    m = SetupMiddleware(lambda r: HttpResponse('Ok'))
    response = m(request)

    assert response.status_code == 200


@override_config(INITIALIZED=True)
def test_setupmiddleware_call_configured(rf):
    request = rf.get('/')
    m = SetupMiddleware(lambda r: HttpResponse('Ok'))
    response = m(request)

    assert response.status_code == 200
