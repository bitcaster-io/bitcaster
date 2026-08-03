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

    provider = SocialProviderFactory.create(provider="google")
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


def test_delete(app: DjangoTestApp, context: "Context") -> None:
    from bitcaster.models import SocialProvider

    url = reverse("admin:social_socialprovider_delete", args=[context["provider"].pk])
    res: "TestResponse" = app.get(url)
    assert res.status_code == 200
    frm = next(f for f in res.forms.values() if "post" in f.fields)
    res = frm.submit()
    assert res.status_code == 302
    assert not SocialProvider.objects.filter(pk=context["provider"].pk).exists()


def test_delete_own_login_provider_forbidden(app: DjangoTestApp, context: "Context") -> None:
    from testutils.factories import SocialAccountFactory

    from bitcaster.models import SocialProvider

    SocialAccountFactory.create(user=app._user, provider=str(context["provider"].pk))
    url = reverse("admin:social_socialprovider_delete", args=[context["provider"].pk])
    res: "TestResponse" = app.get(url, expect_errors=True)
    assert res.status_code == 403
    assert SocialProvider.objects.filter(pk=context["provider"].pk).exists()


def test_disable(app: DjangoTestApp, context: "Context") -> None:
    url = reverse("admin:social_socialprovider_change", args=[context["provider"].pk])
    res: "TestResponse" = app.get(url)
    frm = res.forms["socialprovider_form"]
    frm["enabled"] = False
    res = frm.submit()
    assert res.status_code == 302
    context["provider"].refresh_from_db()
    assert context["provider"].enabled is False


def test_disable_own_login_provider_forbidden(app: DjangoTestApp, context: "Context") -> None:
    from testutils.factories import SocialAccountFactory

    SocialAccountFactory.create(user=app._user, provider=str(context["provider"].pk))
    url = reverse("admin:social_socialprovider_change", args=[context["provider"].pk])
    res: "TestResponse" = app.get(url)
    frm = res.forms["socialprovider_form"]
    frm["enabled"] = False
    res = frm.submit()
    assert res.status_code == 200
    assert "You cannot disable the SSO provider used by your own account." in res.text
    context["provider"].refresh_from_db()
    assert context["provider"].enabled is True


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
