from typing import TYPE_CHECKING, Any, TypedDict

import pytest
from django.urls import reverse
from testutils.factories import OrganizationFactory

from bitcaster.constants import bitcaster

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import Channel, Message, Organization, Project

    Context = TypedDict(
        "Context",
        {"organization": Organization, "channel": Channel, "message": Message},
    )


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", db: Any) -> "DjangoTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context() -> "Context":
    from testutils.factories import ChannelFactory, MessageFactory

    o = OrganizationFactory()
    ch: Channel = ChannelFactory(organization=o)
    o.channel_set.add(ch)
    message: Message = MessageFactory(channel=ch, organization=o, project=None, application=None)

    return {
        "organization": o,
        "channel": ch,
        "message": message,
    }


def test_protected_org(app: "DjangoTestApp") -> None:
    dl = OrganizationFactory(name=bitcaster.ORGANIZATION)
    url = reverse("admin:bitcaster_organization_change", args=[dl.pk])
    res = app.get(url)
    frm = res.forms["organization_form"]

    assert "name" not in frm.fields
    assert not res.pyquery("a.deletelink")


def test_current(app: "DjangoTestApp", organization: "Organization") -> None:
    url = reverse("admin:bitcaster_organization_current")
    res = app.get(url)
    assert res.status_code == 302
    assert res.location == reverse("admin:bitcaster_organization_change", args=[organization.pk])


def test_current_add(app: "DjangoTestApp") -> None:
    url = reverse("admin:bitcaster_organization_current")
    res = app.get(url)
    assert res.status_code == 302
    assert res.location == reverse("admin:bitcaster_organization_add")


def test_create_project_if_does_not_exists(app: "DjangoTestApp", organization: "Organization") -> None:
    url = reverse("admin:bitcaster_organization_change", args=[organization.pk])
    res = app.get(url)
    res = res.click("Project", linkid="btn-project")
    assert res.status_code == 302
    assert res.location == f"{reverse('admin:bitcaster_project_add')}?organization={organization.pk}"


def test_goto_project_if_exists(app: "DjangoTestApp", project: "Project") -> None:
    url = reverse("admin:bitcaster_organization_change", args=[project.organization.pk])
    res = app.get(url)
    res = res.click("Project", linkid="btn-project")
    assert res.status_code == 302
    assert res.location == reverse("admin:bitcaster_project_change", args=[project.pk])
