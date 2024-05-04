from constance.test import override_config
from django.http import HttpResponse
from django.utils import timezone


@override_config()
def test_useragent(db, rf):
    from bitcaster.middleware.user_agent import UserAgentMiddleware

    request = rf.get("/", headers={"Content_Type": "text/html", "User-Agent": "Test-Agent %s" % timezone.now()})
    m = UserAgentMiddleware(lambda x: HttpResponse(""))
    m(request)
    assert request.user_agent


@override_config()
def test_useragent_missing(db, rf):
    from bitcaster.middleware.user_agent import UserAgentMiddleware

    request = rf.get("/", headers={"Content_Type": "text/html", "User-Agent": ""})
    m = UserAgentMiddleware(lambda x: HttpResponse(""))
    m(request)
    assert request.user_agent
