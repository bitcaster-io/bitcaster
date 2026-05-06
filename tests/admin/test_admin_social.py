from typing import TYPE_CHECKING, TypedDict

import pytest

from django.urls import reverse
from django_webtest import DjangoTestApp

if TYPE_CHECKING:
    from webtest.response import TestResponse

    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import SocialProvider, User

    Context = TypedDict("Context", {"provider": SocialProvider})


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> DjangoTestApp:
    django_app: DjangoTestApp = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context() -> "Context":
    from testutils.factories import SocialProviderFactory

    from bitcaster.social.models import Provider

    provider = SocialProviderFactory.create(provider=Provider.GOOGLE)
    return {"provider": provider}


def test_add(app: DjangoTestApp) -> None:
    url = reverse("admin:social_socialprovider_add")
    res: "TestResponse" = app.get(url)
    frm = res.forms["socialprovider_form"]

    frm["label"] = "Google"
    frm["provider"] = "google"
    res = frm.submit()
    assert res.status_code == 302


def test_change(app: DjangoTestApp, context: "Context") -> None:
    url = reverse("admin:social_socialprovider_change", args=[context["provider"].pk])
    res: "TestResponse" = app.get(url)
    frm = res.forms["socialprovider_form"]
    frm["label"] = "Google 2"
    res = frm.submit()
    assert res.status_code == 302


def test_validate_unique(app: DjangoTestApp) -> None:
    url = reverse("admin:social_socialprovider_add")
    res: "TestResponse" = app.get(url)
    res.forms["socialprovider_form"]["label"] = "Google"
    res.forms["socialprovider_form"]["provider"] = "google"
    res = res.forms["socialprovider_form"].submit()
    assert res.status_code == 302
    res: "TestResponse" = app.get(url)
    res.forms["socialprovider_form"]["label"] = "Google"
    res.forms["socialprovider_form"]["provider"] = "google"
    res = res.forms["socialprovider_form"].submit()
    assert res.status_code == 200


def test_write_only_widgets(app: DjangoTestApp) -> None:
    from bitcaster.models import SocialProvider

    url = reverse("admin:social_socialprovider_add")
    res: "TestResponse" = app.get(url)
    frm = res.forms["socialprovider_form"]
    frm["label"] = "Google"
    frm["provider"] = "google"
    frm["secret"] = "123"
    res = frm.submit()
    assert res.status_code == 302
    instance = SocialProvider.objects.get(provider="google")
    assert instance.secret == "123"
    url = reverse("admin:social_socialprovider_change", args=[instance.pk])
    res: "TestResponse" = app.get(url)
    frm = res.forms["socialprovider_form"]
    res = frm.submit()
    assert res.status_code == 302
    instance.refresh_from_db()
    assert instance.secret == "123"
