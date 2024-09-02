import json
from typing import TYPE_CHECKING, Any
from unittest import mock

import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.urls import reverse
from strategy_field.utils import fqn
from testutils.factories import ChannelFactory

from bitcaster.models.protocols import CreateMessage

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables
    from pytest import FixtureRequest, MonkeyPatch
    from responses import RequestsMock

    from bitcaster.models import Channel, Message


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", db: Any) -> "DjangoTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture()
def messages(db: Any) -> None:
    from testutils.factories import MessageFactory, NotificationFactory

    n = NotificationFactory()
    MessageFactory(notification=n)


@pytest.fixture()
def email_message(email_channel: "Channel") -> "Message":
    from testutils.factories import MessageFactory

    from bitcaster.dispatchers import SystemDispatcher

    return MessageFactory(channel=ChannelFactory(dispatcher=fqn(SystemDispatcher)))


def test_render(app: "DjangoTestApp", message: "Message") -> None:
    opts: "Options[Message]" = message._meta
    url = reverse(admin_urlname(opts, "render"), args=[message.pk])  # type: ignore[arg-type]
    res = app.post(url, {"content": "{{a}}", "content_type": "text/html", "context": json.dumps({"a": "333"})})
    assert res.content == b"333"


def test_render_text(app: "DjangoTestApp", message: "Message") -> None:
    opts: "Options[Message]" = message._meta
    url = reverse(admin_urlname(opts, "render"), args=[message.pk])  # type: ignore[arg-type]
    res = app.post(url, {"content": "{{a}}", "content_type": "text/plain", "context": json.dumps({"a": "333"})})
    assert res.content == b"<pre>333</pre>"


def test_render_error(app: "DjangoTestApp", message: "Message") -> None:
    opts: "Options[Message]" = message._meta
    url = reverse(admin_urlname(opts, "render"), args=[message.pk])  # type: ignore[arg-type]
    res = app.post(url, {"content": "{{a}}", "content_type": "text/html", "context": "--"})
    assert res.content == b"<!DOCTYPE HTML>* context\n  * Enter a valid JSON."


def test_edit(app: "DjangoTestApp", message: "Message") -> None:
    new_subject_value = "subject_update_value"
    new_content_value = "content_update_value"
    new_html_content_value = "html_content_update_value"

    opts: "Options[Message]" = message._meta
    url = reverse(admin_urlname(opts, "edit"), args=[message.pk])  # type: ignore[arg-type]

    res = app.get(url)
    assert res.status_code == 200
    assert new_subject_value not in str(res.content)  # Sanity check
    assert new_content_value not in str(res.content)  # Sanity check
    assert new_html_content_value not in str(res.content)  # Sanity check

    res = app.post(
        url,
        {
            "subject": new_subject_value,
            "content": new_content_value,
            "html_content": new_html_content_value,
            "context": "{}",
        },
    )
    assert res.status_code == 302

    message.refresh_from_db()
    assert message.subject == new_subject_value
    assert message.content == new_content_value
    assert message.html_content == new_html_content_value

    refresh_res = app.get(url)
    assert refresh_res.status_code == 200
    assert new_subject_value in refresh_res.text
    assert new_content_value in refresh_res.text
    assert new_html_content_value in refresh_res.text


def test_send_message(
    app: "DjangoTestApp", email_message: "Message", mailoutbox: list[Any], mocked_responses: "RequestsMock"
) -> None:
    opts: "Options[Message]" = email_message._meta
    url = reverse(admin_urlname(opts, "send_message"), args=[email_message.pk])  # type: ignore[arg-type]

    res = app.post(
        url,
        {
            "recipient": "test@example.com",
            "subject": "subject",
            "content": "content",
            "html_content": "html_content",
            "context": "{}",
        },
    )
    assert res.status_code == 200
    assert res.json == {"success": "message sent"}
    assert len(mailoutbox) == 1


def test_send_message_fail(
    app: "DjangoTestApp",
    email_message: "Message",
    mailoutbox: list[Any],
    mocked_responses: "RequestsMock",
    monkeypatch: "MonkeyPatch",
) -> None:
    opts: "Options[Message]" = email_message._meta
    url = reverse(admin_urlname(opts, "send_message"), args=[email_message.pk])  # type: ignore[arg-type]

    with mock.patch("bitcaster.dispatchers.SystemDispatcher.send", return_value=False):
        res = app.post(
            url,
            {
                "recipient": "test",
                "subject": "subject",
                "content": "content",
                "html_content": "html_content",
                "context": "{}",
            },
        )
    assert res.status_code == 200
    assert res.json == {"error": "Failed to send message to test"}
    assert len(mailoutbox) == 0


def test_send_message_invalid(
    app: "DjangoTestApp",
    email_message: "Message",
    mailoutbox: list[Any],
    mocked_responses: "RequestsMock",
    monkeypatch: "MonkeyPatch",
) -> None:
    opts: "Options[Message]" = email_message._meta
    url = reverse(admin_urlname(opts, "send_message"), args=[email_message.pk])  # type: ignore[arg-type]

    with mock.patch("bitcaster.dispatchers.SystemDispatcher.send", return_value=False):
        res = app.post(
            url,
            {
                "recipient": "xx",
                "subject": "",
                "content": "",
                "html_content": "",
                "context": "--",
            },
        )
    assert res.status_code == 200
    assert res.json == {"error": {"context": ["Enter a valid JSON."]}}
    assert len(mailoutbox) == 0


def test_edit_error(app: "DjangoTestApp", message: "Message") -> None:
    opts: "Options[Message]" = message._meta
    url = reverse(admin_urlname(opts, "edit"), args=[message.pk])  # type: ignore[arg-type]
    res = app.get(url)
    assert res.status_code == 200
    res = app.post(
        url,
        {"subject": "subject", "content": "content", "html_content": "html_content", "context": "--"},
    )
    assert res.status_code == 200


def test_add(app: "DjangoTestApp", message: "Message") -> None:
    from testutils.factories import ChannelFactory, NotificationFactory

    opts: "Options[Message]" = message._meta
    url = reverse(admin_urlname(opts, "add"))  # type: ignore[arg-type]
    res = app.get(url)
    assert res.status_code == 200
    res = app.post(
        url,
        {
            "channel": ChannelFactory().pk,
            "notification": NotificationFactory().pk,
            "name": "name",
        },
    )
    assert res.status_code == 302, res.context["adminform"].form.errors


@pytest.fixture(params=["notification", "event", "application", "project", "organization"])
def level(request: "FixtureRequest") -> "Channel":
    return request.getfixturevalue(request.param)


def test_changelist(app: "DjangoTestApp", level: CreateMessage, channel: "Channel") -> None:
    owner = level
    message: "Message" = owner.create_message(name=f"Message {type(owner).__name__}", channel=channel)

    url = reverse(admin_urlname(message._meta, "changelist"))  # type: ignore[arg-type]
    res = app.get(url)
    assert res.pyquery("#result_list tbody tr th a").text() == message.name


def test_usage(app: "DjangoTestApp", level: CreateMessage, channel: "Channel") -> None:
    owner: CreateMessage = level
    message: "Message" = owner.create_message(name=f"Message {type(owner).__name__}", channel=channel)
    opts: "Options[Message]" = message._meta

    url = reverse(admin_urlname(opts, "usage"), args=[message.pk])  # type: ignore[arg-type]
    res = app.get(url)
    assert res.pyquery("#usage tbody tr td a").text() == owner.name
