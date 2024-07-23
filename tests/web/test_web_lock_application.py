from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables

from bitcaster.constants import Bitcaster
from bitcaster.forms.locking import LockingModeChoice
from bitcaster.models import Application, User

if TYPE_CHECKING:

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "other_project": Application,
            "app2": Application,
            "bitcaster_app": Application,
            "app_locked": Application,
        },
    )


@pytest.fixture
def context(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "Context":
    from testutils.factories.org import (
        ApplicationFactory,
        OrganizationFactory,
        ProjectFactory,
    )

    bitcaster_org = OrganizationFactory(name=Bitcaster.ORGANIZATION)
    bitcaster_project = ProjectFactory(organization=bitcaster_org)

    app1 = ApplicationFactory()
    app2 = ApplicationFactory(project=app1.project)
    app_locked = ApplicationFactory(project=app1.project, locked=True)
    app3 = ApplicationFactory()
    app4 = ApplicationFactory(project=bitcaster_project)

    return {"app": app1, "other_project": app3, "app2": app2, "bitcaster_app": app4, "app_locked": app_locked}


def test_byapplication(app: DjangoTestApp, context: "Context") -> None:
    from bitcaster.models import Application

    url = reverse("locking")
    res = app.get(url)
    assert res.status_code == 200

    applications = set(Application.objects.filter(locked=True).values_list("id", flat=True))
    assert applications == {context["app_locked"].id}

    res.form["mode-operation"] = LockingModeChoice.PROJECT
    res = res.form.submit()

    assert res.form.fields["project-project"][0].options == [
        ("", True, "All"),
        (str(context["app"].project.id), False, context["app"].project.name),
        (str(context["other_project"].project.id), False, context["other_project"].project.name),
    ]

    res.form.fields["project-project"][0].select(str(context["app"].project.id))
    res = res.form.submit()
    assert res.status_code == 200

    assert res.form.fields["application-application"][0].options == [
        ("", True, "All"),
        (str(context["app"].id), False, context["app"].name),
        (str(context["app2"].id), False, context["app2"].name),
    ]

    res = res.form.submit()
    assert res.status_code == 200

    applications = set(Application.objects.filter(locked=True).values_list("id", flat=True))
    assert applications == {context["app"].id, context["app2"].id, context["app_locked"].id}

    assert "The following applications have been locked" in res.text
    assert context["app_locked"].name not in res.text
    assert context["app"].name in res.text
    assert context["app2"].name in res.text
