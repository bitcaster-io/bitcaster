from typing import TYPE_CHECKING, Any

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import Application, Organization, Project


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", db: Any) -> "DjangoTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_get_readonly_fields(app: "DjangoTestApp", project: "Project", bitcaster: "Application") -> None:
    url = reverse("admin:bitcaster_project_change", args=[project.pk])
    res = app.get(url)
    frm = res.forms["project_form"]
    assert "organization" in frm.fields
    assert "name" in frm.fields

    url = reverse("admin:bitcaster_project_change", args=[bitcaster.project.pk])
    res = app.get(url)
    frm = res.forms["project_form"]
    assert "organization" not in frm.fields
    assert "name" not in frm.fields
    assert "slug" not in frm.fields


def test_add(app: "DjangoTestApp", organization: "Organization", bitcaster: "Application") -> None:
    url = reverse("admin:bitcaster_project_add")
    res = app.get(url)
    frm = res.forms["project_form"]
    frm["name"] = "dummy"
    frm["organization"].force_value(organization.pk)
    frm["owner"].force_value(organization.owner.pk)
    frm["environments"].force_value("development,production")
    res = frm.submit("Save and continue editing")
    assert res.status_code == 302, res.context["adminform"].errors


def test_current(app: "DjangoTestApp", project: "Project") -> None:
    url = reverse("admin:bitcaster_project_current")
    res = app.get(url)
    assert res.status_code == 302
    assert res.location == reverse("admin:bitcaster_project_change", args=[project.pk])
