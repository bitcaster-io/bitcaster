from unittest.mock import MagicMock

import pytest
from pyquery import PyQuery
from social_core.exceptions import AuthException

from bitcaster.middleware.errors import ExceptionHandlingMiddleware


@pytest.fixture
def middleware():
    return ExceptionHandlingMiddleware(MagicMock())


def test_call(rf, middleware):
    request = rf.get("/")
    response = middleware(request)
    assert response


def test_auth_exception_handling(rf, middleware):
    request = rf.get("/")

    exception = AuthException("Test authentication error")

    response = middleware.process_exception(request, exception)

    assert response

    assert response.status_code == 500
    pq = PyQuery(response.content)
    assert pq("#error_code").text() == "500"
    assert pq("#error_message").text() == "AuthException"


def test_other_exception_handling(rf, middleware):
    request = rf.get("/")

    exception = Exception("Test generic error")

    response = middleware.process_exception(request, exception)

    assert not response
