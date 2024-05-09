from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from testutils.factories import OrganizationFactory

from bitcaster.constants import Bitcaster

if TYPE_CHECKING:
    from bitcaster.models import Channel, Message, Organization

    Context = TypedDict(
        "Context",
        {"organization": Organization, "channel": Channel, "message": Message},
    )


@pytest.fixture()
def app(django_app_factory, db):
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


def test_create_template(app, context) -> None:
    channel: "Channel" = context["channel"]
    org: "Organization" = context["organization"]

    url = reverse("admin:bitcaster_organization_templates", args=[org.pk])
    res = app.get(url)
    frm = res.forms["messageForm"]
    frm["name"] = "Test Template"
    frm["channel"] = channel.pk
    frm.submit()

    assert org.message_set.filter(name="Test Template").count() == 1


def test_avoid_duplicates_template(app, context) -> None:
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


def test_protected_org(app) -> None:
    dl = OrganizationFactory(name=Bitcaster.ORGANIZATION)
    url = reverse("admin:bitcaster_organization_change", args=[dl.pk])
    res = app.get(url)
    frm = res.forms["organization_form"]

    assert "name" not in frm.fields
    assert not res.pyquery("a.deletelink")
