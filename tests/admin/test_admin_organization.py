from typing import TYPE_CHECKING, Any, TypedDict

import pytest
from django.urls import reverse
from testutils.factories import GroupFactory, OrganizationFactory
from webtest import Upload

from bitcaster.auth.constants import DEFAULT_GROUP_NAME
from bitcaster.constants import Bitcaster
from bitcaster.models import Channel, Group, Message, Organization, Project

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    Context = TypedDict(
        "Context",
        {"organization": Organization, "channel": Channel, "message": Message},
    )


@pytest.fixture()
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


def test_create_organization_template(app: "DjangoTestApp", context: "Context") -> None:
    channel: "Channel" = context["channel"]
    org: "Organization" = context["organization"]

    url = reverse("admin:bitcaster_organization_templates", args=[org.pk])
    res = app.get(url)
    frm = res.forms["messageForm"]
    frm["name"] = "Test Organization Template"
    frm["channel"] = channel.pk
    frm.submit()

    assert org.message_set.filter(name="Test Organization Template").count() == 1


def test_avoid_duplicates_template(app: "DjangoTestApp", context: "Context") -> None:
    message: "Message" = context["message"]
    channel: "Channel" = context["channel"]
    org: "Organization" = context["organization"]

    url = reverse("admin:bitcaster_organization_templates", args=[org.pk])
    res = app.get(url)

    frm = res.forms["messageForm"]
    frm["name"] = message.name
    frm["channel"] = channel.pk
    res = frm.submit(expect_errors=True)
    assert res.status_code == 400

    assert org.message_set.filter(name=message.name).count() == 1


def test_protected_org(app: "DjangoTestApp") -> None:
    dl = OrganizationFactory(name=Bitcaster.ORGANIZATION)
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


def test_import_user_from_file(app: "DjangoTestApp") -> None:
    org: Organization = OrganizationFactory()
    grp: Group = GroupFactory(name=DEFAULT_GROUP_NAME)
    url = reverse("admin:bitcaster_organization_import_from_file", args=[org.pk])
    res = app.get(url)
    frm = res.forms["action-form"]
    res = frm.submit()
    assert res.status_code == 200

    frm["group"] = grp.pk
    frm["file"] = Upload(
        "data.csv",
        (
            b"email,first_name,last_name\n"
            b"user1@example.com,FirstName1,LastName1\n"
            b"user2@example.com,FirstName2,LastName2\n"
            b"user3@example.com,FirstName3,LastName3\n"
        ),
    )
    res = frm.submit()

    assert res.status_code == 302, res.context["form"].errors
    assert org.users.filter(email="user1@example.com").exists()
