# mypy: disable-error-code="union-attr"
from typing import TYPE_CHECKING, Any, Generator
from unittest.mock import Mock, patch

import pytest
from constance.test.unittest import override_config
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.http import HttpRequest
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.safestring import SafeString
from django_webtest import DjangoTestApp, DjangoWebtestResponse
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from pytest_factoryboy import LazyFixture, register
from strategy_field.utils import fqn
from testutils.factories import (
    AssignmentFactory,
    ChannelFactory,
    OrganizationFactory,
    ProjectFactory,
    UserFactory,
    UserRoleFactory,
)

from bitcaster.admin.channel import ChannelType
from bitcaster.models import Channel
from bitcaster.state import state

if TYPE_CHECKING:
    from webtest.forms import Form as WebTestForm

    from bitcaster.models import Project, UserRole

register(UserFactory)
register(OrganizationFactory)
register(ChannelFactory, "channel")
register(ProjectFactory, "project")


@pytest.fixture()
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


@pytest.fixture()
def gmail_channel(db: Any) -> Channel:
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    return ChannelFactory(
        dispatcher=fqn(GMailDispatcher),
        config={"username": "username", "password": "password"},
    )


@pytest.fixture()
def channel_template(gmail_channel: "Channel") -> Channel:
    from testutils.factories.channel import ChannelFactory

    from bitcaster.dispatchers import GMailDispatcher

    return ChannelFactory(
        dispatcher=fqn(GMailDispatcher),
        organization=gmail_channel.organization,
        project=None,
        config={"username": "username", "password": "password"},
    )


@pytest.fixture()
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


# @pytest.mark.wizard
# def test_create_abstract_channel(app: DjangoTestApp, gmail_channel: "Channel") -> None:
#     url = reverse("admin:bitcaster_channel_add")
#     res = app.get(url)
#     res.forms["channel-add"]["mode-operation"] = ChannelType.MODE_TEMPLATE
#     res = res.forms["channel-add"].submit()
#     res.forms["channel-add"]["org-organization"] = gmail_channel.organization.pk
#     res = res.forms["channel-add"].submit()
#     res.forms["channel-add"]["data-name"] = "Channel-1"
#     res = res.forms["channel-add"].submit()
#     assert res.status_code == 302
#     assert Channel.objects.filter(
#         name="Channel-1",
#         organization=gmail_channel.organization,
#         project=None,
#         parent=None,
#     ).exists()


@pytest.mark.wizard
def test_add_create_abstract_for_org(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    # Create Abstract Channel for provided organization
    url = reverse("admin:bitcaster_channel_add")
    res: DjangoWebtestResponse = app.get(
        f"{url}?mode={ChannelType.MODE_TEMPLATE}&organization={gmail_channel.organization.pk}"
    )
    res.forms["channel-add"]["data-name"] = "Channel-1"
    frm: "WebTestForm" = res.forms["channel-add"]
    assert res.pyquery("#btn-finish")
    assert not res.pyquery("#btn-next")
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

    res.forms["channel-add"]["mode-operation"] = "new"
    res = res.forms["channel-add"].submit()
    res.forms["channel-add"]["data-name"] = "Channel-1"
    res = res.forms["channel-add"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(
        name="Channel-1",
        organization=gmail_channel.organization,
        project=gmail_channel.project,
        parent=None,
    ).exists()


@pytest.mark.wizard
def test_inherit_channel_for_project(app: DjangoTestApp, channel_template: "Channel") -> None:
    # Create Program Channel for provided project
    project: Project = ProjectFactory(organization=channel_template.organization)
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(f"{url}?mode=inherit&project={project.pk}")
    res.forms["channel-add"]["parent-parent"] = channel_template.pk
    res.forms["channel-add"]["parent-name"] = "Channel-2"
    res = res.forms["channel-add"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(
        name="Channel-2",
        organization=channel_template.organization,
        project=project,
        parent=channel_template,
    ).exists()


@pytest.mark.wizard
def test_add_new_channel(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(url)
    res.forms["channel-add"]["mode-operation"] = ChannelType.MODE_NEW
    res = res.forms["channel-add"].submit()
    res.forms["channel-add"]["org-organization"] = gmail_channel.organization.pk
    res = res.forms["channel-add"].submit()
    res.forms["channel-add"]["prj-project"] = gmail_channel.project.pk
    res = res.forms["channel-add"].submit()
    res.forms["channel-add"]["data-name"] = "Channel-1"
    res = res.forms["channel-add"].submit()
    assert res.status_code == 302
    assert Channel.objects.filter(
        name="Channel-1",
        organization=gmail_channel.organization,
        project=gmail_channel.project,
        parent=None,
    ).exists()


@pytest.mark.wizard
@pytest.mark.parametrize(
    "back_url,expected",
    [
        ("/admin/bitcaster/user/", "/admin/bitcaster/user/"),
        ("http://url/", reverse("admin:bitcaster_channel_changelist")),
        ("", reverse("admin:bitcaster_channel_changelist")),
    ],
)
def test_add_new_channel_abort(app: DjangoTestApp, gmail_channel: "Channel", back_url: str, expected: str) -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(f"{url}?_from={back_url}")
    res.forms["channel-add"]["mode-operation"] = ChannelType.MODE_NEW
    res = res.forms["channel-add"].submit()
    res.forms["channel-add"]["org-organization"] = gmail_channel.organization.pk
    res = res.forms["channel-add"].submit()
    res.forms["channel-add"]["prj-project"] = gmail_channel.project.pk
    res = res.forms["channel-add"].submit()
    res.forms["channel-add"]["data-name"] = "Channel-1"
    res = res.forms["channel-add"].submit("wizard_cancel")
    assert res.status_code == 302
    assert res.location == expected
    assert not Channel.objects.filter(name="Channel-1").exists()


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


@pytest.mark.wizard
def test_add_channel_tampered_with(app: DjangoTestApp, gmail_channel: "Channel") -> None:
    url = reverse("admin:bitcaster_channel_add")
    res = app.get(url)
    res.forms["channel-add"]["mode-operation"].force_value("missing")
    res = res.forms["channel-add"].submit()
    assert res.status_code == 200


@pytest.mark.parametrize("flt", ["abstract", "project", ""])
def test_add_channel_filter_by_type(
    app: DjangoTestApp, gmail_channel: "Channel", channel_template: "Channel", flt: str
) -> None:
    url = reverse("admin:bitcaster_channel_changelist")
    res = app.get(f"{url}?type={flt}")
    assert res.status_code == 200
