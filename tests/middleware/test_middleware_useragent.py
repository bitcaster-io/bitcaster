from typing import TYPE_CHECKING

import pytest
from django.http import HttpResponse
from django.test.client import RequestFactory
from django.utils import timezone

if TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest

pytestmarker = pytest.mark.django_db


def test_useragent(rf: RequestFactory) -> None:
    from bitcaster.middleware.user_agent import UserAgentMiddleware

    request: "WSGIRequest" = rf.get(
        "/", headers={"Content_Type": "text/html", "User-Agent": "Test-Agent %s" % timezone.now()}
    )
    m = UserAgentMiddleware(lambda x: HttpResponse(""))
    m(request)
    assert request.user_agent  # type: ignore[attr-defined]


def test_useragent_missing(rf: RequestFactory) -> None:
    from bitcaster.middleware.user_agent import UserAgentMiddleware

    request: "WSGIRequest" = rf.get("/", headers={"Content_Type": "text/html", "User-Agent": ""})
    m = UserAgentMiddleware(lambda x: HttpResponse(""))
    m(request)
    assert request.user_agent  # type: ignore[attr-defined]
