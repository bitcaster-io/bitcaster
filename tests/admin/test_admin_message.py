import json

import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.db.models.options import Options
from django.urls import reverse
from django_webtest import DjangoTestApp

from bitcaster.models import Message


@pytest.fixture()
def app(django_app_factory, db):
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture()
def messages(django_app_factory, db):
    from testutils.factories import MessageFactory, NotificationFactory

    n = NotificationFactory()
    MessageFactory(notification=n)


def test_render(app: DjangoTestApp, message):
    opts: Options = Message._meta
    url = reverse(admin_urlname(opts, "render"), args=[message.pk])
    res = app.post(url, {"content": "{{a}}", "content_type": "text/html", "context": json.dumps({"a": "333"})})
    assert res.content == b"333"


def test_render_text(app: DjangoTestApp, message):
    opts: Options = Message._meta
    url = reverse(admin_urlname(opts, "render"), args=[message.pk])
    res = app.post(url, {"content": "{{a}}", "content_type": "text/plain", "context": json.dumps({"a": "333"})})
    assert res.content == b"<pre>333</pre>"


def test_render_error(app: DjangoTestApp, message):
    opts: Options = Message._meta
    url = reverse(admin_urlname(opts, "render"), args=[message.pk])
    res = app.post(url, {"content": "{{a}}", "content_type": "text/html", "context": "--"})
    assert res.content == b"<!DOCTYPE HTML>* context\n  * Enter a valid JSON."


def test_edit(app: DjangoTestApp, message):
    opts: Options = Message._meta
    url = reverse(admin_urlname(opts, "edit"), args=[message.pk])
    res = app.get(url)
    assert res.status_code == 200
    res = app.post(
        url,
        {
            "subject": "subject",
            "content": "content",
            "html_content": "html_content",
            "content_type": "text/html",
            "context": "{}",
        },
    )
    assert res.status_code == 302
    message.refresh_from_db()
    assert message.subject == "subject"
    assert message.content == "content"
    assert message.html_content == "html_content"


def test_edit_error(app: DjangoTestApp, message):
    opts: Options = Message._meta
    url = reverse(admin_urlname(opts, "edit"), args=[message.pk])
    res = app.get(url)
    assert res.status_code == 200
    res = app.post(
        url,
        {"subject": "subject", "content": "content", "html_content": "html_content", "context": "--"},
    )
    assert res.status_code == 200


def test_add(app: DjangoTestApp, message):
    from testutils.factories import ChannelFactory, NotificationFactory

    opts: Options = Message._meta
    url = reverse(admin_urlname(opts, "add"))
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
def level(request):
    return request.getfixturevalue(request.param)


def test_changelist(request, app: DjangoTestApp, level, channel):
    opts: Options = Message._meta
    owner = level
    message = owner.create_message(name=f"Message {type(owner).__name__}", channel=channel)

    url = reverse(admin_urlname(opts, "changelist"))
    res = app.get(url)
    assert res.pyquery("#result_list tbody tr th a").text() == message.name


def test_usage(request, app: DjangoTestApp, level, channel):
    opts: Options = Message._meta
    owner = level
    message = owner.create_message(name=f"Message {type(owner).__name__}", channel=channel)

    url = reverse(admin_urlname(opts, "usage"), args=[message.pk])
    res = app.get(url)
    assert res.pyquery("#usage tbody tr td a").text() == owner.name
