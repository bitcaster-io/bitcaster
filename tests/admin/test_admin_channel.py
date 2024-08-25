from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

import pytest
from constance.test.unittest import override_config
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.http import HttpRequest
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.safestring import SafeString
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from pytest_factoryboy import LazyFixture, register
from strategy_field.utils import fqn
from testutils.factories import (
    AssignmentFactory,
    ChannelFactory,
    OrganizationFactory,
    ProjectFactory,
    UserFactory,
)

from bitcaster.models import Channel
from bitcaster.state import state

if TYPE_CHECKING:
    from bitcaster.models import Organization, Project

register(UserFactory)
register(OrganizationFactory)
register(ChannelFactory, "channel")
register(ProjectFactory, "project")


@pytest.fixture()
def app(django_app_factory: MixinWithInstanceVariables, rf: RequestFactory, db: Any) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    request: HttpRequest = rf.get("/")
    request.user = admin_user
    with state.configure(request=request):
        yield django_app


@pytest.fixture()
def gmail_channel(db: Any) -> Channel:
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    return ChannelFactory(dispatcher=fqn(GMailDispatcher), config={"username": "username", "password": "password"})


@pytest.fixture()
def system_channel(db: Any) -> Channel:
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    ch = ChannelFactory(
        dispatcher=fqn(GMailDispatcher),
        name="system-channel",
        config={"username": "username", "password": "password"},
    )
    with override_config(SYSTEM_EMAIL_CHANNEL=ch.pk):
        yield ch


@pytest.mark.parametrize("channel__project", [None, LazyFixture(ProjectFactory)])
def test_change(app: DjangoTestApp, channel: Channel) -> None:
    url = reverse(admin_urlname(Channel._meta, SafeString("change")), args=[channel.pk])
    res = app.get(url)
    res = res.forms["channel_form"].submit()
    assert res.status_code == 302


def test_configure(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    opts: Options[Channel] = Channel._meta
    url = reverse(admin_urlname(opts, SafeString("configure")), args=[gmail_channel.pk])
    res = app.get(url)
    assert res.status_code == 200

    res = app.post(url, {"username": "", "password": ""})
    assert res.status_code == 200

    res = app.post(url, {"username": "username", "password": "password"})
    assert res.status_code == 302


def test_test_404(app: DjangoTestApp) -> None:
    opts: Options[Channel] = Channel._meta
    url = reverse(admin_urlname(opts, SafeString("test")), args=[-1])
    res = app.get(url, expect_errors=True)
    assert res.status_code == 404


def test_test(app: DjangoTestApp, gmail_channel: Channel) -> None:
    opts: Options[Channel] = Channel._meta
    url = reverse(admin_urlname(opts, SafeString("test")), args=[gmail_channel.pk])
    res = app.get(url)
    assert res.status_code == 200
    AssignmentFactory(channel=gmail_channel, address__user=app._user)

    app.post(url, {"recipient": "", "subject": "", "": ""})
    assert res.status_code == 200

    with patch("smtplib.SMTP", autospec=True) as mock:
        res = app.post(url, {"recipient": "recipient", "subject": "subject", "message": "message"})
    assert res.status_code == 200

    mock.assert_called()
    s: Mock = mock.return_value
    s.login.assert_called()
    s.starttls.assert_called()
    s.sendmail.assert_called()


def test_get_readonly_if_default(app: DjangoTestApp, system_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_change", args=[system_channel.pk])
    res = app.get(url)
    frm = res.forms["channel_form"]
    assert "name" not in frm.fields


def test_get_readonly_fields(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_change", args=[gmail_channel.pk])
    res = app.get(url)
    res.forms["channel_form"]["name"] = "abc"
    res = res.forms["channel_form"].submit()
    assert res.status_code == 302


def test_add_new_channel_for_single_project(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(url)
    # step 1
    res.forms["channel-add"]["mode-operation"] = "new"
    res = res.forms["channel-add"].submit()
    # step 2
    res.forms["channel-add"]["org-organization"] = gmail_channel.organization.pk
    res = res.forms["channel-add"].submit()
    # step 3
    res.forms["channel-add"]["prj-project"] = gmail_channel.project.pk
    res = res.forms["channel-add"].submit()
    # step 5
    res.forms["channel-add"]["data-name"] = "Channel-1"
    res = res.forms["channel-add"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(
        name="Channel-1",
        organization=gmail_channel.organization,
        project=gmail_channel.project,
    ).exists()


def test_add_new_channel_for_all_projects(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(url)
    # step 1
    res.forms["channel-add"]["mode-operation"] = "new"
    res = res.forms["channel-add"].submit()
    # step 2
    res.forms["channel-add"]["org-organization"] = gmail_channel.organization.pk
    res = res.forms["channel-add"].submit()
    # step 3
    res.forms["channel-add"]["prj-project"] = ""
    res = res.forms["channel-add"].submit()
    # step 5
    res.forms["channel-add"]["data-name"] = "Channel-1"
    res = res.forms["channel-add"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(name="Channel-1", project__isnull=True).exists()


def test_add_new_channel_inherit(app: "DjangoTestApp", gmail_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(url)
    # step 1
    res.forms["channel-add"]["mode-operation"] = "inherit"
    res = res.forms["channel-add"].submit()
    # step 2
    res.forms["channel-add"]["parent-parent"] = gmail_channel.pk
    res.forms["channel-add"]["parent-name"] = "Channel-2"
    res.forms["channel-add"]["parent-project"] = gmail_channel.project.pk
    res = res.forms["channel-add"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(name="Channel-2", project=gmail_channel.project).exists()


def test_add_new_channel_for_specific_organization(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(f"{url}?organization={gmail_channel.organization.pk}")

    res.forms["channel-add"]["prj-project"] = gmail_channel.project.pk
    res = res.forms["channel-add"].submit()
    res.forms["channel-add"]["data-name"] = "Channel-1"
    res = res.forms["channel-add"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(
        name="Channel-1",
        organization=gmail_channel.organization,
        project=gmail_channel.project,
    ).exists()


def test_add_new_channel_for_specific_project(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(f"{url}?project={gmail_channel.project.pk}")
    # step 1
    res.forms["channel-add"]["mode-operation"] = "new"
    res = res.forms["channel-add"].submit()
    # step 2
    assert res.forms["channel-add"]["org-organization"].value == str(gmail_channel.project.organization.pk)
    res = res.forms["channel-add"].submit()
    # step 3
    assert res.forms["channel-add"]["prj-project"].value == str(gmail_channel.project.pk)
    res = res.forms["channel-add"].submit()
    # res.forms["channel-add"]["prj-project"] = gmail_channel.project.pk
    # res = res.forms["channel-add"].submit()
    # step 4
    res.forms["channel-add"]["data-name"] = "Channel-1"
    res = res.forms["channel-add"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(
        name="Channel-1",
        organization=gmail_channel.organization,
        project=gmail_channel.project,
    ).exists()


def test_add_new_channel_with_invalid_organization(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    organization: "Organization" = OrganizationFactory(owner__is_staff=True)
    url = reverse("admin:bitcaster_channel_add")
    app.set_user(organization.owner)

    res = app.get(f"{url}?organization={gmail_channel.organization.pk}", expect_errors=True)
    assert res.status_code == 403


def test_add_new_channel_with_invalid_project(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    organization: "Organization" = OrganizationFactory(owner__is_staff=True)
    project: "Project" = ProjectFactory(organization=organization, owner=organization.owner)
    url = reverse("admin:bitcaster_channel_add")
    app.set_user(project.organization.owner)

    res = app.get(f"{url}?project={gmail_channel.project.pk}", expect_errors=True)
    assert res.status_code == 403
