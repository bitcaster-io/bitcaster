import pytest
from django.http import HttpResponse

from bitcaster.middleware.security import SecurityHeadersMiddleware


@pytest.mark.parametrize('header', ['X_DEBUG', 'X-Frame-Options', 'X-Content-Type-Options',
                                    'X-XSS-Protection'])
def test_securityheadersmiddleware_add(rf, header):
    request = rf.get('/')
    response = HttpResponse('Ok')
    response[header] = 'value'
    m = SecurityHeadersMiddleware(lambda r: response)
    assert m(request)
