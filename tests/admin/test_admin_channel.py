# mypy: disable-error-code="union-attr"
from typing import TYPE_CHECKING, Any, Generator
from unittest.mock import Mock, patch

import pytest
from constance.test.unittest import override_config
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.safestring import SafeString
from django_webtest import DjangoTestApp, DjangoWebtestResponse
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from strategy_field.utils import fqn
from testutils.factories import (
    AssignmentFactory,
    UserRoleFactory,
)
from testutils.helpers import assert_form_error

from bitcaster.models import Channel, Project
from bitcaster.state import state

if TYPE_CHECKING:
    from django.db.models.options import Options
    from django.http import HttpRequest
    from webtest.forms import Form as WebTestForm

    from bitcaster.models import UserRole


@pytest.fixture
def app(django_app_factory: MixinWithInstanceVariables, rf: RequestFactory, gmail_channel: "Channel") -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    request: HttpRequest = rf.get("/")
    request.user = admin_user
    UserRoleFactory(organization=gmail_channel.organization, user=admin_user)

    with state.configure(request=request):
        yield django_app


@pytest.fixture
def gmail_channel(db: Any) -> Channel:
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    return ChannelFactory(
        dispatcher=fqn(GMailDispatcher),
        config={"username": "username", "password": "password", "timeout": 3},
    )


@pytest.fixture
def alien_channel(db: Any) -> Channel:
    from testutils.factories import ChannelFactory, OrganizationFactory

    from bitcaster.dispatchers import GMailDispatcher

    return ChannelFactory(
        organization=OrganizationFactory(name="alien"),
        dispatcher=fqn(GMailDispatcher),
        config={"username": "username", "password": "password", "timeout": 3},
    )


@pytest.fixture
def channel_template(gmail_channel: "Channel") -> Channel:
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    return ChannelFactory(
        dispatcher=fqn(GMailDispatcher),
        organization=gmail_channel.organization,
        project=None,
        config={"username": "username", "password": "password"},
    )


@pytest.fixture
def system_channel(db: Any) -> Generator[Channel, None, None]:
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    ch: Channel = ChannelFactory(
        dispatcher=fqn(GMailDispatcher),
        name="system-channel",
        config={"username": "username", "password": "password"},
    )
    with override_config(SYSTEM_EMAIL_CHANNEL=ch.pk):
        yield ch


def test_configure(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    opts: Options[Channel] = Channel._meta
    url = reverse(admin_urlname(opts, SafeString("configure")), args=[gmail_channel.pk])
    res = app.get(url)
    assert res.status_code == 200

    res = app.post(url, {"username": "", "password": ""})
    assert res.status_code == 200

    res = app.post(url, {"username": "username", "password": "password", "timeout": 3})
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


@pytest.mark.wizard
def test_add_create_abstract_for_org(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    # Create Abstract Channel for provided organization
    url = reverse("admin:bitcaster_channel_add")
    res: DjangoWebtestResponse = app.get(f"{url}?organization={gmail_channel.organization.pk}")
    frm: "WebTestForm" = res.forms["channel_form"]
    frm["name"] = "Channel-1"
    res = frm.submit()
    assert res.status_code == 302
    assert Channel.objects.filter(
        name="Channel-1",
        organization=gmail_channel.organization,
        project=None,
        parent=None,
    ).exists()


@pytest.mark.wizard
def test_add_new_channel_for_project(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    # Create Program Channel for provided project
    url = reverse("admin:bitcaster_channel_add")
    res: DjangoWebtestResponse = app.get(f"{url}?project={gmail_channel.project.pk}")
    frm: "WebTestForm" = res.forms["channel_form"]
    frm.submit()
    frm["organization"] = gmail_channel.project.organization.pk
    frm["name"] = "Channel-1"
    res = frm.submit()
    assert res.status_code == 302, res.context["adminform"].form.errors
    assert Channel.objects.filter(
        name="Channel-1",
        organization=gmail_channel.organization,
        project=gmail_channel.project,
        parent=None,
    ).exists()


@pytest.mark.wizard
def test_inherit_channel_for_project(app: DjangoTestApp, channel_template: "Channel") -> None:
    # Create Program Channel for provided project
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(f"{url}?organization={channel_template.organization.pk}")
    res.forms["channel_form"]["parent"].force_value(channel_template.pk)
    res.forms["channel_form"]["name"] = "Channel-2"
    res = res.forms["channel_form"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(
        name="Channel-2",
        organization=channel_template.organization,
        project=None,
        parent=channel_template,
    ).exists()


@pytest.mark.wizard
def test_add_new_channel(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(url)
    res = res.forms["channel_form"].submit()
    assert_form_error(res, "name", "This field is required.")

    res.forms["channel_form"]["organization"] = gmail_channel.organization.pk
    res.forms["channel_form"]["project"].force_value(gmail_channel.project.pk)
    res.forms["channel_form"]["name"] = "Channel-1"
    res = res.forms["channel_form"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(
        name="Channel-1",
        organization=gmail_channel.organization,
        project=gmail_channel.project,
        parent=None,
    ).exists()


@pytest.mark.wizard
def test_channel_consistency(app: DjangoTestApp, gmail_channel: "Channel", project: "Project") -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(url)
    res.forms["channel_form"]["organization"] = gmail_channel.organization.pk
    res.forms["channel_form"]["project"].force_value(project.pk)
    res.forms["channel_form"]["name"] = "Channel-1"
    res = res.forms["channel_form"].submit()
    assert_form_error(res, "project", "Project does not belong selected organization.")


@pytest.mark.wizard
def test_add_channel_permission(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    r: UserRole = UserRoleFactory()
    assert r.organization != gmail_channel.organization
    url = reverse("admin:bitcaster_channel_add")
    app.set_user(r.user)

    res = app.get(f"{url}?mode=template&organization={gmail_channel.organization.pk}", expect_errors=True)
    assert res.status_code == 403

    res = app.get(f"{url}?mode=template&project={gmail_channel.project.pk}", expect_errors=True)
    assert res.status_code == 403


@pytest.mark.parametrize("flt", ["abstract", "project", ""])
def test_add_channel_filter_by_type(
    app: DjangoTestApp, gmail_channel: "Channel", channel_template: "Channel", flt: str
) -> None:
    url = reverse("admin:bitcaster_channel_changelist")
    res = app.get(f"{url}?type={flt}")
    assert res.status_code == 200


def test_add_channel_with_parent(
    app: DjangoTestApp,
    alien_channel: "Channel",
    channel_template: "Channel",
) -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(url)
    res.forms["channel_form"]["organization"] = channel_template.organization.pk
    res.forms["channel_form"]["parent"].force_value(alien_channel.pk)
    res.forms["channel_form"]["name"] = "Channel-2"
    res = res.forms["channel_form"].submit()
    assert res.status_code == 200
    assert_form_error(res, "parent", "Parent does not belong same organization.")
