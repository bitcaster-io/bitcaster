from constance.test import override_config
from django.http import HttpResponse


@override_config()
def test_useragent(db, rf):
    from bitcaster.middleware.user_agent import UserAgentMiddleware

    request = rf.get("/", headers={"HTT_Content_Type": "text/html"})
    m = UserAgentMiddleware(lambda x: HttpResponse(""))
    m(request)
    assert request.user_agent
