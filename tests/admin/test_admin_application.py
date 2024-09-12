from typing import Any

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from bitcaster.models import Application, Project


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

    from bitcaster.constants import Bitcaster

    return ApplicationFactory(
        name=Bitcaster.APPLICATION, project__name=Bitcaster.PROJECT, project__organization__name=Bitcaster.ORGANIZATION
    )


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


def test_add(app: "DjangoTestApp", project: "Project", bitcaster: "Application") -> None:
    url = reverse("admin:bitcaster_application_add")
    res = app.get(url)
    frm = res.forms["application_form"]
    frm["name"] = "App #1"
    frm["project"].force_value(project.pk)
    res = frm.submit()
    assert res.status_code == 302
