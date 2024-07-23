from typing import Any

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from bitcaster.models import Application


@pytest.fixture()
def app(django_app_factory: MixinWithInstanceVariables, db: Any) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture()
def application(db: Any) -> Application:
    from testutils.factories import ApplicationFactory

    return ApplicationFactory()


@pytest.fixture()
def bitcaster(db: Any) -> "Application":
    from testutils.factories import ApplicationFactory

    return ApplicationFactory(name="bitcaster")


def test_get_readonly_fields(app: "DjangoTestApp", application: "Application", bitcaster: "Application") -> None:
    url = reverse("admin:bitcaster_application_change", args=[application.pk])
    res = app.get(url)
    frm = res.forms["application_form"]
    assert "project" in frm.fields
    assert "name" in frm.fields

    url = reverse("admin:bitcaster_application_change", args=[bitcaster.pk])
    res = app.get(url)
    frm = res.forms["application_form"]
    assert "project" not in frm.fields
    assert "name" not in frm.fields
    assert "slug" not in frm.fields
