from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp

if TYPE_CHECKING:
    from webtest.response import TestResponse

    from bitcaster.models import SocialProvider

    Context = TypedDict("Context", {"provider": SocialProvider})


@pytest.fixture()
def app(django_app_factory, admin_user) -> DjangoTestApp:
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_edit(app: DjangoTestApp, validation, settings) -> None:
    settings.ROOT_TOKEN_HEADER = "abc"
    settings.ROOT_TOKEN = "123"
    url = reverse("admin:bitcaster_validation_change", args=[validation.pk])

    res: "TestResponse" = app.get(f"{url}?user={app._user.pk}")
    assert res
