import os
from typing import TYPE_CHECKING, Any
from unittest import mock

import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.urls import reverse
from django.utils.safestring import SafeString
from django_webtest import DjangoTestApp, DjangoWebtestResponse
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from freezegun import freeze_time
from testutils.factories import ApiKeyFactory

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Application


@pytest.fixture()
def app(django_app_factory: MixinWithInstanceVariables, db: Any) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture()
def api_key(db: Any) -> "ApiKey":
    from testutils.factories import ApiKeyFactory, ApplicationFactory

    a: "Application" = ApplicationFactory(
        project__environments=["development"], project__name=f"Project {os.environ.get('PYTEST_XDIST_WORKER', '')}"
    )
    return ApiKeyFactory(application=a, project=a.project, organization=a.project.organization)


def test_edit(app: DjangoTestApp, api_key: "ApiKey") -> None:
    opts: Options[ApiKey] = api_key._meta
    url = reverse(admin_urlname(opts, SafeString("change")), args=[api_key.pk])
    res = app.get(url)
    assert res.status_code == 200

    res.forms["apikey_form"]["grants"] = [Grant.EVENT_TRIGGER, Grant.FULL_ACCESS]
    res = res.forms["apikey_form"].submit()
    assert res.status_code == 302
    api_key.refresh_from_db()
    assert sorted(api_key.grants) == [Grant.EVENT_TRIGGER, Grant.FULL_ACCESS]


def test_add(app: DjangoTestApp, api_key: "ApiKey") -> None:
    opts: Options[ApiKey] = api_key._meta
    url = reverse(admin_urlname(opts, SafeString("add")))
    res = app.get(url)
    assert res.status_code == 200

    res.forms["apikey_form"]["organization"].force_value(api_key.organization.pk)
    res.forms["apikey_form"]["name"] = "Key-1"
    res.forms["apikey_form"]["grants"] = [Grant.FULL_ACCESS]
    res = res.forms["apikey_form"].submit()
    assert res.status_code == 302
    res = res.follow()
    assert res.status_code == 200


def test_add_trigger_required_app(app: DjangoTestApp, api_key: "ApiKey") -> None:
    opts: Options[ApiKey] = api_key._meta
    url = reverse(admin_urlname(opts, SafeString("add")))
    res = app.get(url)
    assert res.status_code == 200

    res.forms["apikey_form"]["organization"].force_value(api_key.organization.pk)
    res.forms["apikey_form"]["name"] = "Key-1"
    res.forms["apikey_form"]["grants"] = [Grant.EVENT_TRIGGER]
    res = res.forms["apikey_form"].submit()
    assert res.status_code == 200
    res.forms["apikey_form"]["name"] = "Key-1"


def test_add_check_environments(app: "DjangoTestApp", api_key: "ApiKey") -> None:
    url = reverse("admin:bitcaster_apikey_add")
    res = app.get(url)
    frm = res.forms["apikey_form"]
    frm["name"] = "Not2"
    res = frm.submit(expect_errors=True)
    assert res.status_code == 200
    assert res.context["adminform"].form.errors == {"organization": ["This field is required."]}
    # add missing fields
    res = app.get(url)
    frm = res.forms["apikey_form"]
    frm["application"].force_value(api_key.application.pk)
    res = frm.submit().follow()

    obj = res.context["original"]
    url = obj.get_admin_change()

    res = app.get(url)
    res.forms["apikey_form"]["environments"] = ["development"]
    res = res.forms["apikey_form"].submit()
    assert res.status_code == 302, res.context["adminform"].form.errors


@pytest.mark.parametrize("flt", ["development", ""])
def test_add_channel_filter_by_type(app: DjangoTestApp, api_key: "ApiKey", flt: str) -> None:
    url = reverse("admin:bitcaster_apikey_changelist")
    res = app.get(f"{url}?env={flt}")
    assert res.status_code == 200


@pytest.mark.parametrize("root", [True, False])
def test_show_key(app: DjangoTestApp, root: bool) -> None:
    with freeze_time("2012-01-14"):
        api_key: "ApiKey" = ApiKeyFactory()
    url = reverse("admin:bitcaster_apikey_show_key", args=[api_key.pk])
    with mock.patch("bitcaster.admin.api_key.is_root", lambda s: root):
        res: DjangoWebtestResponse = app.get(url)
        assert (api_key.key in res.text) is root
