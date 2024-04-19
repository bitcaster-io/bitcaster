from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from webtest.response import TestResponse

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event

    Context = TypedDict(
        "Context",
        {
            "group1": Channel,
            "group2": Event,
        },
    )


@pytest.fixture()
def app(django_app_factory, admin_user) -> DjangoTestApp:
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context() -> "Context":
    from testutils.factories import SocialProviderFactory

    provider = SocialProviderFactory()
    return {"provider": provider}


def test_get_readonly_if_default(app: DjangoTestApp, context: "Context", settings) -> None:
    settings.ROOT_TOKEN_HEADER = "abc"
    url = reverse("admin:social_socialprovider_change", args=[context["provider"].pk])

    res: TestResponse = app.get(url)
    frm = res.forms["socialprovider_form"]
    assert "configuration" not in frm.fields
    res = app.get(url, extra_environ={"HTTP_ABC": settings.ROOT_TOKEN})
    frm = res.forms["socialprovider_form"]
    assert "configuration" in frm.fields