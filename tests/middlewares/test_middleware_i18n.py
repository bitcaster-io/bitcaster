from unittest.mock import Mock

from django.http import HttpResponse

from bitcaster.middleware.i18n import UserLanguageMiddleware


def test_userlanguagemiddleware_call(rf, settings):
    request = rf.get('/aaa/', HTTP_REFERER='/from/')
    request.user = Mock(is_authenticated=True, language='it_IT')

    m = UserLanguageMiddleware(lambda r: HttpResponse('Ok'))
    response = m(request)
    assert response.cookies[settings.LANGUAGE_COOKIE_NAME].value == 'it_IT'


def test_userlanguagemiddleware_anonymous(rf, settings):
    request = rf.get('/aaa/', HTTP_REFERER='/from/')
    request.user = Mock(is_authenticated=False)

    m = UserLanguageMiddleware(lambda r: HttpResponse('Ok'))
    response = m(request)
    assert settings.LANGUAGE_COOKIE_NAME not in response.cookies
