import pytest
from unittest.mock import MagicMock

from bitcaster.middleware.errors import ExceptionHandlingMiddleware


@pytest.fixture
def middleware():
    return ExceptionHandlingMiddleware(MagicMock())


def test_call(rf, middleware):
    request = rf.get("/")
    response = middleware(request)
    assert response
