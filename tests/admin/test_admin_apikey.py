from typing import TYPE_CHECKING

import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.urls import reverse
from django_webtest import DjangoTestApp

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import ApiKey


@pytest.fixture()
def app(django_app_factory, db):
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_edit(app: DjangoTestApp, api_key: "ApiKey"):
    opts: Options = api_key._meta
    url = reverse(admin_urlname(opts, "change"), args=[api_key.pk])
    res = app.get(url)
    assert res.status_code == 200

    res.forms["apikey_form"]["grants"] = [Grant.EVENT_TRIGGER, Grant.EVENT_ADMIN]
    res = res.forms["apikey_form"].submit()
    assert res.status_code == 302
    api_key.refresh_from_db()
    assert sorted(api_key.grants) == [Grant.EVENT_ADMIN, Grant.EVENT_TRIGGER]
